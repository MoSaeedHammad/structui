import argparse
import sys
from structui.app import run_app

def main():
    parser = argparse.ArgumentParser(description="StructUI Configuration Editor")
    parser.add_argument("--dir", type=str, default=".", help="Directory containing config files")
    parser.add_argument("--schema", type=str, default=".structui_schema.yaml", help="Path to schema file")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the UI on (default: 8080)")
    
    args = parser.parse_args()
    
    try:
        run_app(data_dir=args.dir, schema_filepath=args.schema, port=args.port)
    except Exception as e:
        print(f"Error starting StructUI: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ in {"__main__", "__mp_main__"}:
    main()
