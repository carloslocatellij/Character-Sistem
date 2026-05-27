from PIL import Image

img = Image.open('the_begin_2.png')

nsize = (160, 100)

resimg = img.resize(nsize, Image.Resampling.LANCZOS)

imagem_rgb = resimg.convert('RGB')

imagem_rgb.save('the_begin_1.jpg')