import cv2


# the class for storing some information of a loaded image
class LoadedImageInfo:
    def __init__(self, orig_img, processed_img=None):
        self.processed_img = processed_img
        self.orig_img = orig_img


# the class of a dictionary for all loaded images
class LoadedImagesDict:
    # the dictionary of all loaded images
    # key, value: win_name, loaded-image-info
    loaded_images = dict()
    saved_paths = dict()
    sr_out_paths = dict()

    def __init__(self):
        pass

    @classmethod
    def update_sr_out_path(self, win_name, sr_out_path):
        self.sr_out_paths[win_name] = str(sr_out_path)

    @classmethod
    def get_sr_out_path(self, win_name):
        return self.sr_out_paths[win_name]

    @classmethod
    def update_save_path(self, win_name, save_path):
        self.saved_paths[win_name] = str(save_path)

    @classmethod
    def get_save_path(self, win_name):
        return self.saved_paths[win_name]

    # add a new processed image
    @classmethod
    def add_processed_image(self, win_name, orig_img, new_img=None):
        info = LoadedImageInfo(orig_img, new_img)
        self.loaded_images[win_name] = info

    # update the processed image
    @classmethod
    def update_processed_image(self, win_name, updated_img):
        self.loaded_images[win_name].processed_img = updated_img

    # get the processed image by its name
    @classmethod
    def get_processed_image(self, win_name):
        if win_name in self.loaded_images:
            return self.loaded_images[win_name].processed_img
        else:
            return None

    # get the original image by its name
    @classmethod
    def get_original_image(self, win_name):
        if win_name in self.loaded_images:
            return cv2.copyMakeBorder(self.loaded_images[win_name].orig_img, 0, 0, 0, 0, cv2.BORDER_REPLICATE)
        else:
            return None

    # get the current size of the processed image
    @classmethod
    def get_size_of_processed_image(self, win_name):
        img = self.get_processed_image(win_name)
        if img is None:
            return None
        return img.shape[1], img.shape[0]
