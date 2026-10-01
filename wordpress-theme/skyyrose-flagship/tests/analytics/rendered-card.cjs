/** Real theme markup with synthetic product data; authentication not applicable. */
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const theme = path.resolve(__dirname, '../..');

module.exports = () =>
  execFileSync(
    process.env.PHP_BIN || 'php',
    [
      '-r',
      `
define('ABSPATH', '${theme}');
class WC_Product {
  function get_id() { return 9; }
  function get_name() { return 'Fixture product'; }
  function get_price_html() { return '$1'; }
  function get_sku() { return 'fixture-001'; }
}
function sanitize_title($v) { return strtolower($v); }
function esc_attr($v) { return htmlspecialchars($v, ENT_QUOTES); }
function esc_html($v) { return htmlspecialchars($v, ENT_QUOTES); }
function esc_url($v) { return htmlspecialchars($v, ENT_QUOTES); }
function esc_attr_e($v, $d) { echo esc_attr($v); }
function esc_html_e($v, $d) { echo esc_html($v); }
function __($v, $d) { return $v; }
function wp_kses_post($v) { return $v; }
function absint($v) { return abs((int) $v); }
function disabled($v) { if ($v) { echo 'disabled'; } }
function skyyrose_render_picture($url, $title, $options) { return '<img src="' . esc_url($url) . '" alt="' . esc_attr($title) . '">'; }
function get_template_part($slug, $name, $args) { include '${theme}/' . $slug . '.php'; }
get_template_part('template-parts/product-card-holo', null, array(
  'product' => new WC_Product(), 'collection' => 'fixture',
  'image_url' => '/fixture.jpg', 'image_back' => '/fixture-back.jpg', 'permalink' => '/product/fixture/'
));
`,
    ],
    { encoding: 'utf8' }
  );
