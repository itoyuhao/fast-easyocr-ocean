from PIL import Image


def resize_image(image_path, output_path, width, height):
    """
    將圖片調整為指定的寬度和高度。

    Args:
        image_path (str): 輸入圖片的路徑。
        output_path (str): 調整大小後的圖片輸出路徑。
        width (int): 目標寬度。
        height (int): 目標高度。
    """
    with Image.open(image_path) as image:
        resized_image = image.resize((width, height))
        resized_image.save(output_path)