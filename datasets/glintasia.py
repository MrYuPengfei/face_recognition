from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import glob
import os

import cv2
import numpy as np
from tqdm import tqdm
import torch.utils.data as data
try:
    from transform import opencv_transforms as cv_transforms
except:
    from .transform import opencv_transforms as cv_transforms


class GlintAsia(data.Dataset):
    def __init__(self, image_root='data', annotation_folder=None, phase="train", cur_id=0):
        super(GlintAsia, self).__init__()
        self.image_root = image_root
        self.database_name = "GlintAsia"
        self.phase = phase
        self.cur_id = cur_id
        self.person_id_container = list()
        self.person_id2label = {}
        self.data_list = list()
        self.transforms = cv_transforms.Compose([
            cv_transforms.RandomRotation(30),
            cv_transforms.RandomResizedCrop(112, (0.8, 1.0)),
            cv_transforms.ColorJitter(brightness=0.2,
                                      contrast=0.15,
                                      saturation=0.1,
                                      hue=0),
            cv_transforms.RandomHorizontalFlip(),
            # cv_transforms.RandomGrayscale(),
            cv_transforms.ToTensor(),
            cv_transforms.ColorAugmentation(),
            cv_transforms.RandomErasing(sl=0.02, sh=0.2),
            cv_transforms.Normalize([0.4914, 0.4822, 0.4465],
                                    [0.247, 0.243, 0.261])
        ])
        self._prepare(self.image_root, direction=0)
        self.person_id2label = {idx: label + self.cur_id for label, idx in enumerate(self.person_id_container)}

    def __len__(self):
        return len(self.data_list)

    def class_num(self):
        return len(self.person_id_container)

    def _prepare(self, image_dir, direction=0):
        print(f"Loading {self.database_name} images...")
        self.data_list = glob.glob(image_dir + "/*/*.jpg")
        for person_id_folder in tqdm(os.listdir(image_dir)):
            person_id = person_id_folder.split('_')[-1]
            if int(person_id) == -1:
                continue  # junk images are just ignored
            assert 0 <= int(person_id) <= 200000
            person_id = '_'.join([self.database_name, person_id])
            if person_id not in self.person_id_container:
                self.person_id_container.append(person_id)

    def __getitem__(self, index):
        data_index = self.data_list[index]
        image_path = data_index
        person_id = os.path.basename(os.path.dirname(image_path))
        person_id = person_id.split('_')[-1]
        person_id = '_'.join([self.database_name, person_id])
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8()), 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, dsize=(112, 112))
        img = self.transforms(img)
        target = self.person_id2label[person_id]
        return img, target


def test():
    image_root = r"/home/heroin/datasets/faces_glintasia_images"
    train_dataset = GlintAsia(image_root)
    train_data_loader = data.DataLoader(dataset=train_dataset,
                                        batch_size=64,
                                        shuffle=False,
                                        num_workers=0,
                                        drop_last=True
                                        )
    print(train_dataset.person_id_container)
    for images, targets in train_data_loader:
        # print(images.data.cpu().numpy()[:, :, 0:10, 0:10])
        print(targets)
        exit(1)


if __name__ == '__main__':
    test()
