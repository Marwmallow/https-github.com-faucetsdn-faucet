#!/usr/bin/env python3
"""
Topaz Video AI Batch Helper
Генерирует команды для batch обработки в Topaz Video AI
"""

import argparse
from pathlib import Path
import json


def generate_topaz_commands(input_files: list, resolution: str = "4k", model: str = "artemis-lq"):
    """
    Generate Topaz Video AI batch commands

    Args:
        input_files: List of video files to process
        resolution: Target resolution (1080p, 1440p, 4k)
        model: Topaz AI model to use
    """

    # Resolution mapping
    resolutions = {
        '720p': '1280x720',
        '1080p': '1920x1080',
        '1440p': '2560x1440',
        '2k': '2560x1440',
        '4k': '3840x2160',
        'uhd': '3840x2160',
    }

    target_res = resolutions.get(resolution.lower(), '1920x1080')

    # Topaz models with descriptions
    models_info = {
        'artemis-lq': 'Low Quality Enhancement (YouTube, compressed video)',
        'artemis-mq': 'Medium Quality Enhancement',
        'artemis-hq': 'High Quality Enhancement (clean source)',
        'proteus': 'Realistic Enhancement',
        'iris': 'Old/Interlaced Footage',
        'gaia-hq': 'High Quality Upscaling',
        'gaia-cg': 'CGI/Animation'
    }

    print("=" * 60)
    print("🎬 TOPAZ VIDEO AI BATCH COMMANDS")
    print("=" * 60)
    print(f"Model: {model} - {models_info.get(model, 'Unknown')}")
    print(f"Target: {target_res}")
    print(f"Files: {len(input_files)}")
    print("=" * 60)
    print()

    # Windows batch file
    batch_content = "@echo off\n"
    batch_content += "REM Topaz Video AI Batch Processing\n"
    batch_content += f"REM Model: {model}\n"
    batch_content += f"REM Resolution: {target_res}\n\n"

    # Unix shell script
    shell_content = "#!/bin/bash\n"
    shell_content += "# Topaz Video AI Batch Processing\n"
    shell_content += f"# Model: {model}\n"
    shell_content += f"# Resolution: {target_res}\n\n"

    for i, file in enumerate(input_files, 1):
        input_path = Path(file)
        output_name = f"{input_path.stem}_topaz_{model}_{resolution}.mp4"
        output_path = input_path.parent / "topaz_output" / output_name

        print(f"[{i}/{len(input_files)}] {input_path.name}")
        print(f"         → {output_name}")

        # Windows command
        win_cmd = (
            f'echo Processing {input_path.name}...\n'
            f'"C:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\tvai.exe" '
            f'-i "{input_path}" '
            f'-o "{output_path}" '
            f'-m {model} '
            f'-s {target_res} '
            f'--quality high\n\n'
        )
        batch_content += win_cmd

        # Unix command
        unix_cmd = (
            f'echo "Processing {input_path.name}..."\n'
            f'"/Applications/Topaz Video AI.app/Contents/MacOS/Topaz Video AI" '
            f'-i "{input_path}" '
            f'-o "{output_path}" '
            f'-m {model} '
            f'-s {target_res} '
            f'--quality high\n\n'
        )
        shell_content += unix_cmd

    batch_content += "echo Done!\npause\n"
    shell_content += 'echo "Done!"\n'

    # Save batch files
    Path("topaz_output").mkdir(exist_ok=True)

    with open("topaz_batch.bat", "w") as f:
        f.write(batch_content)

    with open("topaz_batch.sh", "w") as f:
        f.write(shell_content)

    print()
    print("=" * 60)
    print("✅ Batch files created:")
    print("   📁 topaz_batch.bat (Windows)")
    print("   📁 topaz_batch.sh (Mac/Linux)")
    print()
    print("📖 How to use:")
    print("   Windows: Double-click topaz_batch.bat")
    print("   Mac/Linux: chmod +x topaz_batch.sh && ./topaz_batch.sh")
    print()
    print("⚠️  Note: Topaz CLI might not work with all versions.")
    print("   Alternative: Use Topaz GUI for batch processing:")
    print("   1. Open Topaz Video AI")
    print("   2. File → Add Multiple Files")
    print("   3. Choose model: " + model)
    print("   4. Set output resolution: " + target_res)
    print("   5. Export All")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Topaz Video AI Batch Helper - Generate batch processing scripts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create batch for all MP4 files in current folder
  python topaz_batch_helper.py *.mp4 -r 4k

  # Use specific model for compressed video
  python topaz_batch_helper.py video1.mp4 video2.mp4 -m artemis-lq -r 1080p

  # Old footage restoration
  python topaz_batch_helper.py old_video.avi -m iris -r 1080p

Topaz Models:
  artemis-lq  - Low quality source (YouTube, compressed) [RECOMMENDED for most]
  artemis-mq  - Medium quality source
  artemis-hq  - High quality clean source
  proteus     - Realistic enhancement
  iris        - Old/interlaced footage restoration
  gaia-hq     - High quality upscaling
  gaia-cg     - CGI/Animation upscaling
        """
    )

    parser.add_argument('files', nargs='+', help='Video files to process')
    parser.add_argument('-r', '--resolution', default='4k',
                        help='Target resolution: 720p, 1080p, 1440p, 4k (default: 4k)')
    parser.add_argument('-m', '--model', default='artemis-lq',
                        help='Topaz AI model (default: artemis-lq)')

    args = parser.parse_args()

    # Validate files
    valid_files = []
    for pattern in args.files:
        files = list(Path('.').glob(pattern))
        if not files:
            # Try as direct path
            if Path(pattern).exists():
                valid_files.append(pattern)
        else:
            valid_files.extend([str(f) for f in files])

    if not valid_files:
        print("❌ No valid video files found")
        return

    generate_topaz_commands(valid_files, args.resolution, args.model)


if __name__ == '__main__':
    main()
