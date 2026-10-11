#!/usr/bin/env bash
set -euo pipefail

# Local, founder-review-only previsualization. This is a fictional SkyyRose
# house tour: it contains no transit operator imagery, marks, audio, maps, or
# claims of affiliation. It is not release media or product-proof authority.
# Historical manual authoring recipe retained for provenance, not a canonical
# build step. Prepare a separately verified source directory containing the exact
# filenames below: the legacy theme has the br-003/br-011 product references,
# while V2 has the br-008/br-009/br-010 on-model media. assets/card-scenes alone
# is not a drop-in input. Obtain source/output approval before running the recipe.

theme_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="$theme_dir/assets/video"
source_frame="${1:?Usage: build-skyyrose-tour-film.sh <historical-reference-frame> <historical-source-directory>}"
model_dir="${2:?Usage: build-skyyrose-tour-film.sh <historical-reference-frame> <historical-source-directory>}"
font_ui="/System/Library/Fonts/Avenir Next Condensed.ttc"

command -v ffmpeg >/dev/null 2>&1 || { echo "ffmpeg is required" >&2; exit 1; }
command -v ffprobe >/dev/null 2>&1 || { echo "ffprobe is required" >&2; exit 1; }
command -v magick >/dev/null 2>&1 || { echo "ImageMagick is required" >&2; exit 1; }

models=(
	"$model_dir/br-003-baseball-classic.jpeg"
	"$model_dir/br-008-onmodel.webp"
	"$model_dir/br-009-onmodel.webp"
	"$model_dir/br-010-onmodel.webp"
	"$model_dir/br-011-the-rose-hockey.png"
)
for required in "$source_frame" "$font_ui" "${models[@]}"; do
	[[ -f "$required" ]] || { echo "Missing required source: $required" >&2; exit 1; }
done

mkdir -p "$output_dir"
render_dir="$(mktemp -d "${TMPDIR:-/tmp}/skyyrose-tour-film.XXXXXX")"
trap 'rm -rf "$render_dir"' EXIT

titles=(
	"00 / BASEBALL CLASSIC"
	"01 / SF INSPIRED"
	"02 / LAST OAKLAND"
	"03 / THE BAY"
	"04 / THE ROSE"
)
chapters=( "FOUNDATION" "SAN FRANCISCO" "OAKLAND" "THE BAY" "SAN JOSE" )

magick "$source_frame" -crop 802x300+0+1325 +repage \
	-resize '1920x1080^' -gravity center -extent 1920x1080 \
	-colorspace sRGB -blur 0x5 -brightness-contrast -28x12 "$render_dir/background.png"

for index in 0 1 2 3 4; do
	frame="$render_dir/frame-$index.png"
	magick "$render_dir/background.png" \
		-fill '#00000080' -draw 'rectangle 0,0 1920,1080' \
		-fill '#050505b8' -stroke '#c9a85e' -strokewidth 2 -draw 'rectangle 88,86 1128,856' \
		-stroke '#c9a85e' -strokewidth 4 -draw 'line 88,86 88,856' \
		\( "${models[$index]}" -resize '650x975>' \) -gravity northeast -geometry +65+52 -composite -gravity northwest \
		-font "$font_ui" -fill '#c9a85e' -pointsize 28 -annotate +132+132 'SKYY ROSE / JERSEY SERIES' \
		-font "$font_ui" -fill white -pointsize 64 -annotate +132+245 'TOUR AROUND THE BAY' \
		-font "$font_ui" -fill '#d6d0c7' -pointsize 24 -annotate +132+315 'OAKLAND  —  SAN FRANCISCO  —  THE BAY  —  SAN JOSE' \
		-fill white -pointsize 44 -annotate +132+430 "${titles[$index]}" \
		-font "$font_ui" -fill '#d6d0c7' -pointsize 34 -annotate +132+525 'Carry every number home.' \
		-font "$font_ui" -fill '#c9a85e' -pointsize 22 -annotate +132+635 'LOCAL REVIEW PREVISUALIZATION' \
		-stroke '#c9a85e' -strokewidth 3 -draw 'line 150,770 1010,770' \
		-fill '#c9a85e' -stroke none -draw 'circle 160,770 172,770 circle 370,770 382,770 circle 580,770 592,770 circle 790,770 802,770 circle 1000,770 1012,770' \
		-font "$font_ui" -fill white -pointsize 19 \
		-annotate +132+826 'FOUNDATION' -annotate +338+826 'SF' -annotate +536+826 'OAKLAND' -annotate +748+826 'THE BAY' -annotate +948+826 'SAN JOSE' \
		-fill '#c9a85e' -pointsize 24 -annotate +132+900 "TOUR CHAPTER / ${chapters[$index]}" "$frame"
done

ffmpeg -hide_banner -loglevel error -y \
	-loop 1 -t 3.6 -i "$render_dir/frame-0.png" -loop 1 -t 3.6 -i "$render_dir/frame-1.png" \
	-loop 1 -t 3.6 -i "$render_dir/frame-2.png" -loop 1 -t 3.6 -i "$render_dir/frame-3.png" \
	-loop 1 -t 3.6 -i "$render_dir/frame-4.png" \
	-filter_complex "[0:v]fps=30,format=yuv420p[v0];[1:v]fps=30,format=yuv420p[v1];[2:v]fps=30,format=yuv420p[v2];[3:v]fps=30,format=yuv420p[v3];[4:v]fps=30,format=yuv420p[v4];[v0][v1]xfade=transition=fade:duration=0.5:offset=3.1[x1];[x1][v2]xfade=transition=fade:duration=0.5:offset=6.2[x2];[x2][v3]xfade=transition=fade:duration=0.5:offset=9.3[x3];[x3][v4]xfade=transition=fade:duration=0.5:offset=12.4,fade=t=in:st=0:d=0.45,fade=t=out:st=15.2:d=0.8,format=yuv420p[outv]" \
	-map "[outv]" -an -r 30 -t 16 -c:v libx264 -preset slow -crf 20 -movflags +faststart \
	"$output_dir/skyyrose-tour-around-the-bay.mp4"
ffmpeg -hide_banner -loglevel error -y -i "$output_dir/skyyrose-tour-around-the-bay.mp4" -an \
	-c:v libvpx-vp9 -crf 34 -b:v 0 -row-mt 1 "$output_dir/skyyrose-tour-around-the-bay.webm"
ffmpeg -hide_banner -loglevel error -y -ss 1.2 -i "$output_dir/skyyrose-tour-around-the-bay.mp4" -frames:v 1 \
	-vf "scale=1280:-2" "$render_dir/poster.png"
magick "$render_dir/poster.png" -quality 86 "$output_dir/skyyrose-tour-around-the-bay-poster.webp"
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 "$output_dir/skyyrose-tour-around-the-bay.mp4"
