import os
import glob
import numpy as np
import torch
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
import cv2 as cv

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
 
trans = transforms.Compose([transforms.RandomCrop((256, 256)),  # 裁剪为256*256的图片
                            transforms.ToTensor(),
                            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                            ])  # 图像增强
def BGRtoRGB(image):
    return cv.cvtColor(image, cv.COLOR_BGR2RGB)  # BGR转RGB

def denorm(tensor, device):  # 反归一化
    std = torch.Tensor([0.229, 0.224, 0.225]).reshape(-1, 1, 1).to(device)
    mean = torch.Tensor([0.485, 0.456, 0.406]).reshape(-1, 1, 1).to(device)
    res = torch.clamp(tensor * std + mean, 0, 1)
    return res


class PreprocessDataset(Dataset):
    def __init__(self, content_dir, style_dir, transforms=trans):
        content_dir_resized = content_dir + '_resized'
        style_dir_resized = style_dir + '_resized'
        os.makedirs(content_dir_resized, exist_ok=True)
        os.makedirs(style_dir_resized, exist_ok=True)
        if len(os.listdir(content_dir_resized)) == 0:
            self._resize(content_dir, content_dir_resized)
        if len(os.listdir(style_dir_resized)) == 0:
            self._resize(style_dir, style_dir_resized)
        content_images_paths = glob.glob((content_dir_resized + '/*'))  # 返回图片路径['content\\000000581909.jpg',...]
        np.random.shuffle(content_images_paths)
        style_images_paths = glob.glob(style_dir_resized + '/*')
        np.random.shuffle(style_images_paths)
        self.images_paths = list(zip(content_images_paths, style_images_paths))
        self.transforms = transforms

    @staticmethod
    def _resize(source_dir, target_dir):
        ImgTypeList = ['jpg', 'JPG', 'bmp', 'png', 'jpeg', 'rgb', 'tif']
        file_names = os.listdir(source_dir)
        for dir_path, dir_names, image_names in os.walk(source_dir):
            print(dir_path, dir_names, image_names)
            for image_name in image_names:
                if image_name.split('.')[-1] in ImgTypeList:  # 说明是图片，往下操作
                    image_path = os.path.join(dir_path, image_name)
                    # image_path.append(image_path)
                    try:
                        image = cv.imread(image_path)  # 读图
                        if len(image.shape) == 3 and image.shape[-1] == 3:  # 只用RGB彩图
                            image = image.astype('float32')
                            max_dim = 512  # 图片分辨率的最长边调节，默认等比缩放使最长边为512
                            shape = image.shape[:-1]  # 取出图片的宽和高
                            short_dim = min(shape)  # 找出最短边
                            scale = max_dim / short_dim  # 算出缩放系数
                            new_shape = np.round(np.array(shape) * scale).astype('int32')  # 算出缩放后的形状
                            image = cv.resize(image, dsize=(new_shape[1], new_shape[0]))  # 对图片进行缩放
                            # print(image.shape)
                            cv.imwrite(os.path.join(target_dir, image_name), image)
                    except:
                        pass

    def __len__(self):
        return len(self.images_paths)

    def __getitem__(self, index):
        content_path, style_path = self.images_paths[index]
        content_image = Image.open(content_path)
        style_image = Image.open(style_path)
        # print(np.array(style_image).shape)
        if self.transforms:
            content_image = self.transforms(content_image)
            style_image = self.transforms(style_image)
        return content_image, style_image
