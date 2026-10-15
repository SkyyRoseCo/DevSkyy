<?php
/**
 * Experience Analyzer — Behavioral Event Storage & Rollup Summaries
 *
 * Stores anonymized behavioral events (scroll, hover, click, cart, exit intent)
 * from the frontend JS module. Provides aggregated summaries for the admin
 * dashboard and personalization engine.
 *
 * No PII is stored — events are keyed by anonymous visitor hash.
 *
 * @package SkyyRose
 * @since   6.5.0
 */

defined( 'ABSPATH' ) || exit;

// phpcs:disable WordPress.DB.PreparedSQL.InterpolatedNotPrepared
//
// Justification: every query in this file uses `{$table}` interpolation only
// for the table name (`$wpdb->prefix . 'skyyrose_analytics'`). The prefix is
// server-controlled and the suffix is a hardcoded literal — never sourced from
// user input. All variable VALUES inside each query use proper `%s`/`%d`/`%f`
// placeholders inside `$wpdb->prepare()`. This is the standard WordPress idiom
// for table names; `%i` would be cleaner but requires WP ≥ 6.2 unconditionally.

/*
--------------------------------------------------------------
 * Event Storage
 *--------------------------------------------------------------*/

/**
 * Store a batch of behavioral events.
 *
 * Each event is validated and sanitized before storage. Invalid events
 * are silently skipped. DB errors do not increment the stored count.
 *
 * @param array  $events      Array of event arrays.
 * @param string $visitor_hash Anonymous visitor identifier.
 * @return int Number of events successfully stored.
 */
function skyyrose_see_store_events( array $events, string $visitor_hash = '' ): int {
	global $wpdb;

	$table  = $wpdb->prefix . 'skyyrose_analytics';
	$today  = current_time( 'Y-m-d' );
	$stored = 0;
	$hash   = sanitize_text_field( $visitor_hash );

	foreach ( $events as $event ) {
		// Validate required fields.
		if ( ! is_array( $event ) ) {
			continue;
		}
		if ( empty( $event['type'] ) || ! is_string( $event['type'] ) ) {
			continue;
		}
		if ( ! isset( $event['ts'] ) || ! is_numeric( $event['ts'] ) ) {
			continue;
		}

		// Sanitize values.
		$event_type   = sanitize_text_field( $event['type'] );
		$event_target = sanitize_text_field( $event['target'] ?? '' );
		$page_type    = sanitize_text_field( $event['pageType'] ?? '' );
		$collection   = sanitize_text_field( $event['collection'] ?? '' );
		$value        = floatval( $event['value'] ?? 0 );

		// Upsert: try UPDATE first, INSERT if no rows affected.
		// phpcs:ignore WordPress.DB.DirectDatabaseQuery
		$updated = $wpdb->query(
			$wpdb->prepare(
				"UPDATE {$table}
				 SET event_count = event_count + 1, event_value = event_value + %f
				 WHERE event_date = %s AND event_type = %s AND event_target = %s
				   AND page_type = %s AND collection_slug = %s AND event_id IS NULL",
				$value,
				$today,
				$event_type,
				$event_target,
				$page_type,
				$collection
			)
		);

		if ( false === $updated ) {
			continue; // DB error on UPDATE.
		}

		if ( 0 === $updated ) {
			// phpcs:ignore WordPress.DB.DirectDatabaseQuery
			$inserted = $wpdb->insert(
				$table,
				array(
					'event_date'      => $today,
					'event_type'      => $event_type,
					'event_target'    => $event_target,
					'page_type'       => $page_type,
					'collection_slug' => $collection,
					'event_count'     => 1,
					'event_value'     => $value,
					'visitor_hash'    => $hash,
				),
				array( '%s', '%s', '%s', '%s', '%s', '%d', '%f', '%s' )
			);
			if ( false === $inserted ) {
				continue; // DB error on INSERT.
			}
		}

		++$stored;
	}

	return $stored;
}

/**
 * Project acknowledged events once, including remote duplicates after a retry.
 *
 * The nullable unique key leaves historical aggregate rows intact. Each new
 * event is one atomic row; a partial local failure is safely repairable without
 * a marker/counter transaction. The key hashes site, environment and event UUID;
 * it is not a visitor identifier. Normal 90-day event retention still applies.
 *
 * @param array  $events Validated events with a full durable acknowledgement.
 * @param string $site_id Server-bound site identity.
 * @param string $environment Server-bound environment.
 * @return int|null Newly projected count, or null on any storage failure.
 */
function skyyrose_see_project_acknowledged_events( array $events, string $site_id, string $environment ): ?int {
	if ( ! defined( 'SKYYROSE_SEE_DB_VERSION' ) || get_option( 'skyyrose_see_db_version' ) !== SKYYROSE_SEE_DB_VERSION ) {
		return null;
	}
	global $wpdb;
	$table  = $wpdb->prefix . 'skyyrose_analytics';
	$stored = 0;
	foreach ( $events as $event ) {
		$key = hash( 'sha256', $site_id . ':' . $environment . ':' . $event['event_id'] );
		// phpcs:ignore WordPress.DB.DirectDatabaseQuery
		$result = $wpdb->query(
			$wpdb->prepare(
				"INSERT INTO {$table} (event_id, event_date, event_type, event_target, page_type, collection_slug, event_count, event_value, visitor_hash)
				 VALUES (%s, %s, %s, %s, %s, %s, 1, 0, '')
				 ON DUPLICATE KEY UPDATE event_id = VALUES(event_id)",
				$key,
				substr( $event['occurred_at'], 0, 10 ),
				'engagement_' . $event['event_type'],
				$event['target'] ?? '',
				$event['page_type'],
				$event['collection'] ?? ''
			)
		);
		if ( false === $result ) {
			return null;
		}
		$stored += 1 === $result ? 1 : 0;
	}
	return $stored;
}

/*
--------------------------------------------------------------
 * Analytics Summaries
 *--------------------------------------------------------------*/

/**
 * Get analytics summary for the admin dashboard.
 *
 * @param int $days Number of days to look back.
 * @return array Summary data.
 */
function skyyrose_see_get_summary( int $days = 30 ): array {
	global $wpdb;

	$table = $wpdb->prefix . 'skyyrose_analytics';
	$since = gmdate( 'Y-m-d', strtotime( "-{$days} days" ) );

	// Total events.
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery
	$total = (int) $wpdb->get_var(
		$wpdb->prepare(
			"SELECT COALESCE(SUM(event_count), 0) FROM {$table} WHERE event_date >= %s",
			$since
		)
	);

	// Events by type.
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery
	$by_type = $wpdb->get_results(
		$wpdb->prepare(
			"SELECT event_type, SUM(event_count) AS total
			 FROM {$table}
			 WHERE event_date >= %s
			 GROUP BY event_type
			 ORDER BY total DESC
			 LIMIT 20",
			$since
		),
		ARRAY_A
	);

	// Collection engagement.
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery
	$by_collection = $wpdb->get_results(
		$wpdb->prepare(
			"SELECT collection_slug, SUM(event_count) AS total
			 FROM {$table}
			 WHERE event_date >= %s AND collection_slug != ''
			 GROUP BY collection_slug
			 ORDER BY total DESC",
			$since
		),
		ARRAY_A
	);

	// Top pages.
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery
	$by_page = $wpdb->get_results(
		$wpdb->prepare(
			"SELECT page_type, SUM(event_count) AS total
			 FROM {$table}
			 WHERE event_date >= %s AND page_type != ''
			 GROUP BY page_type
			 ORDER BY total DESC
			 LIMIT 10",
			$since
		),
		ARRAY_A
	);

	// Daily trend.
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery
	$daily = $wpdb->get_results(
		$wpdb->prepare(
			"SELECT event_date, SUM(event_count) AS total
			 FROM {$table}
			 WHERE event_date >= %s
			 GROUP BY event_date
			 ORDER BY event_date ASC",
			$since
		),
		ARRAY_A
	);

	// Consented session identity lives in the durable backend. This legacy
	// engagement projection cannot measure distinct people, even with old hashes.
	$unique_visitors = null;

	return array(
		'period'                   => $days,
		'total_events'             => $total,
		'unique_visitors'          => $unique_visitors,
		'unique_visitors_status'   => 'unavailable',
		'unique_visitors_evidence' => 'Legacy engagement projection does not measure unique visitors.',
		'by_type'                  => $by_type ?: array(),
		'by_collection'            => $by_collection ?: array(),
		'by_page'                  => $by_page ?: array(),
		'daily_trend'              => $daily ?: array(),
	);
}

/*
--------------------------------------------------------------
 * Cleanup Cron
 *--------------------------------------------------------------*/

/**
 * Delete analytics events older than 90 days.
 */
function skyyrose_see_cleanup_old_events(): void {
	global $wpdb;
	$table  = $wpdb->prefix . 'skyyrose_analytics';
	$cutoff = gmdate( 'Y-m-d', strtotime( '-90 days' ) );

	// phpcs:ignore WordPress.DB.DirectDatabaseQuery
	$wpdb->query(
		$wpdb->prepare( "DELETE FROM {$table} WHERE event_date < %s", $cutoff )
	);
}

// Schedule daily cleanup. wp_schedule_event() must run after WordPress init —
// at file-include scope it can fire before the cron API is fully bootstrapped.
add_action( 'skyyrose_see_daily_cleanup', 'skyyrose_see_cleanup_old_events' );

add_action(
	'init',
	function () {
		if ( ! wp_next_scheduled( 'skyyrose_see_daily_cleanup' ) ) {
			wp_schedule_event( time(), 'daily', 'skyyrose_see_daily_cleanup' );
		}
	}
);
