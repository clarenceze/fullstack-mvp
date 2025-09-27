import os
import shutil
import kagglehub

def main():
    # Kaggle 数据集 ID
    dataset = "gregorut/videogamesales"

    print(f"[INFO] 下载 Kaggle 数据集 {dataset} ...")
    path = kagglehub.dataset_download(dataset)
    print(f"[INFO] 数据集下载完成，路径: {path}")

    # 下载目录下的目标文件
    src_file = os.path.join(path, "vgsales.csv")
    if not os.path.exists(src_file):
        raise FileNotFoundError(f"在下载目录中找不到 vgsales.csv: {src_file}")

    # 项目内的目标目录
    dst_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(dst_dir, exist_ok=True)

    dst_file = os.path.join(dst_dir, "vgsales.csv")

    # 复制文件
    shutil.copy2(src_file, dst_file)
    print(f"[OK] 已复制到 {dst_file}")

if __name__ == "__main__":
    main()
