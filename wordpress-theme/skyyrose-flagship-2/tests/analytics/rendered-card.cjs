const path = require('node:path');
const { execFileSync } = require('node:child_process');
module.exports = () =>
  execFileSync(process.env.PHP_BIN || 'php', [path.join(__dirname, 'rendered-card.php')], { encoding: 'utf8' });
