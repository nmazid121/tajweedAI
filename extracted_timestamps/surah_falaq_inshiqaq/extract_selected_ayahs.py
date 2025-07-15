import json
import os
import glob

SELECTED_AYAHS = {
    113: [1, 2],
    84: [16, 17, 18, 19]
}

def filter_ayahs(data):
    surah_number = data.get('surah_number')
    if surah_number not in SELECTED_AYAHS:
        return None
    ayahs = data.get('ayahs', {})
    filtered_ayahs = {str(k): v for k, v in ayahs.items() if int(k) in SELECTED_AYAHS[surah_number]}
    if not filtered_ayahs:
        return None
    return {
        'surah_number': surah_number,
        'surah_name': data.get('surah_name'),
        'ayahs': filtered_ayahs
    }

def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    selected_dir = os.path.join(folder, 'selected_ayahs')
    os.makedirs(selected_dir, exist_ok=True)

    # Delete all *_selected.json files in the current folder
    deleted = []
    for f in glob.glob(os.path.join(folder, '*_selected.json')):
        os.remove(f)
        deleted.append(f)
    if deleted:
        print('Deleted old _selected.json files:')
        for f in deleted:
            print(f'  {f}')
    else:
        print('No old _selected.json files to delete.')

    files = [f for f in os.listdir(folder) if f.endswith('.json') and not f.endswith('_selected.json') and os.path.isfile(os.path.join(folder, f))]
    saved = []
    for file in files:
        path = os.path.join(folder, file)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        filtered = filter_ayahs(data)
        if filtered:
            out_path = os.path.join(selected_dir, file.replace('.json', '_selected.json'))
            with open(out_path, 'w', encoding='utf-8') as out_f:
                json.dump(filtered, out_f, indent=2, ensure_ascii=False)
            saved.append(out_path)
            print(f'Saved: {out_path}')
        else:
            print(f'Skipped (no selected ayahs): {file}')
    print('\nSummary:')
    print(f'Deleted {len(deleted)} old files.')
    print(f'Saved {len(saved)} new selected ayah files to {selected_dir}')

if __name__ == '__main__':
    main() 