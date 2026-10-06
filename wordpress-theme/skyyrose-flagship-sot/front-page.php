<?php
defined( 'ABSPATH' ) || exit;
$collections = skyyrosesot_collections();
$signature   = $collections['signature'] ?? array();
$hero        = skyyrosesot_first_image( $signature );
get_header();
?>
<main id="primary"><section class="srs-hero">
<?php
if ( $hero ) :
	?>
	<img src="<?php echo esc_url( skyyrosesot_asset_uri( $hero ) ); ?>" alt="" fetchpriority="high" width="1920" height="1080"><?php endif; ?><div><h1><?php esc_html_e( 'SkyyRose', 'skyyrose-flagship-sot' ); ?></h1><a href="#collections"><?php esc_html_e( 'Enter worlds', 'skyyrose-flagship-sot' ); ?></a></div></section><section id="collections" class="srs-section"><header><p><?php esc_html_e( 'Collections', 'skyyrose-flagship-sot' ); ?></p><h2><?php esc_html_e( 'Four worlds. One house.', 'skyyrose-flagship-sot' ); ?></h2></header><div class="srs-rail" tabindex="0" aria-label="<?php esc_attr_e( 'Collection worlds. Scroll horizontally.', 'skyyrose-flagship-sot' ); ?>">
	<?php
	foreach ( $collections as $slug => $collection ) :
		$image  = skyyrosesot_first_image( $collection );
		$lockup = skyyrosesot_lockup( $collection );
		?>
		<?php
		if ( $image ) :
			?>
	<a class="srs-world" href="<?php echo esc_url( home_url( '/collections/' . $slug . '/' ) ); ?>" style="<?php echo esc_attr( skyyrosesot_collection_style( $collection ) ); ?>"><img src="<?php echo esc_url( skyyrosesot_asset_uri( $image ) ); ?>" alt="" loading="lazy" width="1920" height="1080"><span><small><?php echo esc_html( $collection['name'] ); ?></small>
			<?php
			if ( $lockup ) :
				?>
	<img class="srs-world__lockup" src="<?php echo esc_url( skyyrosesot_asset_uri( $lockup ) ); ?>" alt="<?php echo esc_attr( $collection['name'] ); ?>">
				<?php
		else :
			?>
	<strong><?php echo esc_html( $collection['name'] ); ?></strong><?php endif; ?><em><?php echo esc_html( $collection['story']['seed'] ); ?></em><b><?php esc_html_e( 'Enter world →', 'skyyrose-flagship-sot' ); ?></b></span></a><?php endif; ?><?php endforeach; ?></div></section><section class="srs-section"><header><p><?php esc_html_e( 'In rotation', 'skyyrose-flagship-sot' ); ?></p><h2><?php esc_html_e( 'Shop verified pieces.', 'skyyrose-flagship-sot' ); ?></h2></header><?php skyyrosesot_render_products( '', 6 ); ?></section></main>
<?php get_footer(); ?>
