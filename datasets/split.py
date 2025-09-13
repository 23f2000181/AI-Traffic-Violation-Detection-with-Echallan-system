import os, random, shutil

# Paths
base_path = "helmet"   # relative to where script is run
images_path = os.path.join(base_path, "images")
labels_path = os.path.join(base_path, "labels")

train_img = os.path.join(images_path, "train")
val_img = os.path.join(images_path, "val")
train_lbl = os.path.join(labels_path, "train")
val_lbl = os.path.join(labels_path, "val")

# Make dirs
for p in [train_img, val_img, train_lbl, val_lbl]:
    os.makedirs(p, exist_ok=True)

# List all images (support .jpg and .png just in case)
all_images = [f for f in os.listdir(images_path) if f.endswith((".jpg", ".png"))]
random.shuffle(all_images)

split_idx = int(0.8 * len(all_images))  # 80/20 split
train_files = all_images[:split_idx]
val_files = all_images[split_idx:]

def move_files(file_list, target_img, target_lbl):
    for f in file_list:
        # move image
        shutil.move(os.path.join(images_path, f), os.path.join(target_img, f))
        # move corresponding label
        label_file = f.rsplit(".", 1)[0] + ".txt"
        if os.path.exists(os.path.join(labels_path, label_file)):
            shutil.move(os.path.join(labels_path, label_file), os.path.join(target_lbl, label_file))

move_files(train_files, train_img, train_lbl)
move_files(val_files, val_img, val_lbl)

print("✅ Split done:", len(train_files), "train,", len(val_files), "val")
