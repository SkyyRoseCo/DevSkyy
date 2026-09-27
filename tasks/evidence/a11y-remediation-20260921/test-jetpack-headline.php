<?php
$source = file_get_contents('/Users/theceo/.codex/worktrees/abe0/DevSkyy/wordpress-theme/skyyrose-flagship-2/inc/launch-readiness.php');
if (!preg_match('/function skyyrose2_jetpack_sharing_headline_html\([^\n]+\) \{\n.*?\n\}/s', $source, $match)) { throw new RuntimeException('Callback missing'); }
eval($match[0]);
foreach (array('sharing', 'likes') as $context) {
    foreach (array('Like this:', '100% style', '<b>Style & sharing</b>') as $label) {
        $escaped = htmlspecialchars($label, ENT_QUOTES, 'UTF-8');
        $actual = sprintf(skyyrose2_jetpack_sharing_headline_html('<h3 class="sd-title">%s</h3>', $label, $context), $escaped);
        if ($actual !== '<p class="sd-title">' . $escaped . '</p>') { throw new RuntimeException('Label format/escape regression'); }
    }
}
if (skyyrose2_jetpack_sharing_headline_html('<h3>%s</h3>', 'Unrelated', 'unknown') !== '<h3>%s</h3>') { throw new RuntimeException('Unrelated context changed'); }
echo "PASS sharing/likes labels: translated text, percent literal, escaped markup, unrelated context\n";
