import os
import random
import shutil

def balance_dataset():
    """Balance the dataset by keeping only 28 negative samples to match 28 positive samples"""
    
    print("🎯 BALANCING DATASET")
    print("=" * 30)
    
    # Create backup directory
    backup_dir = "negative_samples_backup"
    if not os.path.exists(backup_dir):
        print("Creating backup of all negative samples...")
        shutil.copytree("negative_samples", backup_dir)
        print("✅ Backup created!")
    
    # Count current negative samples
    negative_files = []
    for reciter in os.listdir("negative_samples"):
        reciter_path = os.path.join("negative_samples", reciter)
        if os.path.isdir(reciter_path):
            mp3_files = [f for f in os.listdir(reciter_path) if f.endswith('.mp3')]
            for mp3_file in mp3_files:
                negative_files.append(os.path.join(reciter_path, mp3_file))
    
    print(f"Current negative samples: {len(negative_files)}")
    print(f"Target negative samples: 28")
    
    if len(negative_files) <= 28:
        print("✅ Dataset already balanced or has fewer negatives than needed!")
        return
    
    # Randomly select 28 samples to keep
    random.seed(42)  # For reproducible results
    samples_to_keep = random.sample(negative_files, 28)
    
    print(f"Randomly selecting 28 samples to keep...")
    
    # Remove all negative samples first
    for reciter in os.listdir("negative_samples"):
        reciter_path = os.path.join("negative_samples", reciter)
        if os.path.isdir(reciter_path):
            shutil.rmtree(reciter_path)
    
    # Recreate directory structure and copy selected samples
    kept_count = 0
    for sample_path in samples_to_keep:
        # Extract reciter name from path
        reciter = sample_path.split(os.sep)[1]
        filename = os.path.basename(sample_path)
        json_filename = filename.replace('.mp3', '.json')
        
        # Create reciter directory
        reciter_dir = os.path.join("negative_samples", reciter)
        os.makedirs(reciter_dir, exist_ok=True)
        
        # Copy the selected sample and its JSON
        backup_sample_path = sample_path.replace("negative_samples", "negative_samples_backup")
        backup_json_path = backup_sample_path.replace('.mp3', '.json')
        
        new_sample_path = os.path.join(reciter_dir, filename)
        new_json_path = os.path.join(reciter_dir, json_filename)
        
        if os.path.exists(backup_sample_path):
            shutil.copy2(backup_sample_path, new_sample_path)
            kept_count += 1
        
        if os.path.exists(backup_json_path):
            shutil.copy2(backup_json_path, new_json_path)
    
    print(f"✅ Kept {kept_count} negative samples")
    
    # Verify final count
    final_count = 0
    for reciter in os.listdir("negative_samples"):
        reciter_path = os.path.join("negative_samples", reciter)
        if os.path.isdir(reciter_path):
            mp3_files = [f for f in os.listdir(reciter_path) if f.endswith('.mp3')]
            final_count += len(mp3_files)
    
    print(f"\n📊 FINAL DATASET:")
    print(f"Positive samples: 28")
    print(f"Negative samples: {final_count}")
    print(f"Total samples: {28 + final_count}")
    print(f"Ratio: 1:1 (balanced!)")
    
    if final_count == 28:
        print("\n🎉 Dataset perfectly balanced!")
    else:
        print(f"\n⚠️ Warning: Expected 28 negative samples, got {final_count}")

if __name__ == "__main__":
    balance_dataset() 