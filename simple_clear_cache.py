"""
Simple cache clearing script without heavy dependencies
"""

import os
import shutil

def clear_cache():
    """Clear various cache directories"""
    cache_dirs = [
        '__pycache__',
        '.cache',
        'charts_output',
        'static/charts'
    ]
    
    cleared_count = 0
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                if os.path.isdir(cache_dir):
                    shutil.rmtree(cache_dir)
                    print(f"✅ Cleared directory: {cache_dir}")
                    cleared_count += 1
                else:
                    os.remove(cache_dir)
                    print(f"✅ Removed file: {cache_dir}")
                    cleared_count += 1
            except Exception as e:
                print(f"❌ Error clearing {cache_dir}: {e}")
    
    # Clear Python cache files
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:
            if dir_name == '__pycache__':
                try:
                    shutil.rmtree(os.path.join(root, dir_name))
                    print(f"✅ Cleared __pycache__ in {root}")
                    cleared_count += 1
                    dirs.remove(dir_name)
                except Exception as e:
                    print(f"❌ Error clearing __pycache__ in {root}: {e}")
        
        for file_name in files:
            if file_name.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file_name))
                    print(f"✅ Removed {file_name}")
                    cleared_count += 1
                except Exception as e:
                    print(f"❌ Error removing {file_name}: {e}")
    
    print(f"\n🧹 Cache cleanup complete! {cleared_count} items cleared.")
    print("🔮 Ready for Swiss Ephemeris + Placidus house system!")

if __name__ == "__main__":
    clear_cache()