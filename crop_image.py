from PIL import Image
import os

def add(pixel_1, pixel_2):
    pixel_result = []
    for i in range(len(pixel_1)):
        pixel_result.append(int((pixel_1[i] + pixel_2[i])/2))
    return tuple(pixel_result)

def find_overlap(x_crop, x, min_overlap):
    number = (x - min_overlap) // (x_crop - min_overlap)
    if (number == 1):
        number = 2
    overlap = (number * x_crop - x)/(number-1)
    return number, overlap

def crop(image, width_crop, height_crop, filename):
    width, height = image.size

    if width_crop > (width * 0.8) or height_crop > (height * 0.8):
        new_img = image.resize((width_crop, height_crop))
        new_img.save(filename + '.png', 'png')

    print(width, height)

    min_overlap = 100
    number_width_crop, overlap_width = find_overlap(width_crop, width, min_overlap)
    number_height_crop, overlap_height = find_overlap(height_crop, height, min_overlap)

    # print('Size crop \t', number_width_crop, overlap_width, number_height_crop, overlap_height)

    x1 = 0
    x2 = width_crop
    y1 = 0
    y2 = height_crop

    list_img_size_crop = []

    for i in range(number_width_crop * number_height_crop):
        img_crop = image.crop((x1, y1, x2, y2))
        location = [x1, y1, x2, y2]
        # img_crop.show()
        if filename == None:
            img_crop.show()
        else:
            img_crop.save(filename + '-' + str(i) + '.png', 'png')
        list_img_size_crop.append([img_crop, location])

        if (x2 < width):
            x1 = x1 + width_crop - overlap_width
            x2 = x2 + width_crop - overlap_width
        else:
            if (y2 < height):
                x1 = 0
                x2 = width_crop
                y1 = y1 + height_crop - overlap_height
                y2 = y2 + height_crop - overlap_height
    # print('Size list', len(list_img_size_crop))
    return list_img_size_crop, len(list_img_size_crop)


def merge_image(list_image_crop, size_list, filename):
    number_width = 1
    number_height = 1

    width, height = list_image_crop[0][0].size
    print('width, height', width, height)

    for i in range(1, size_list):
        img = list_image_crop[i]
        if img[1][0] != 0:
            number_width += 1
        else:
            break

    for i in range(1, size_list):
        img = list_image_crop[i]
        if img[1][0] == 0:
            number_height += 1

    print('number width, height', number_width, number_height)
    img1_location = list_image_crop[0][1]
    img2_location = list_image_crop[1][1]
    img3_location = list_image_crop[number_width][1]

    print('location', img1_location, img2_location, img3_location)
    overlap_width = int(img1_location[2] - img2_location[0])
    overlap_height = int(img1_location[3] - img3_location[1])

    print('overlap', overlap_width, overlap_height)

    print('\nTEST')
    for i in list_image_crop:
        print(i)
    list_location_height = []

    print('\nnew_weight', list_image_crop[number_width - 1][1][2])
    print('\nnew_height', list_image_crop[number_height * number_width - 1][1][3])

    total_width = list_image_crop[number_width - 1][1][2]
    total_height = list_image_crop[number_height * number_width - 1][1][3]

    fix_width, fix_height = int(total_width), int(total_height)
    new_image = Image.new('RGB', (fix_width, fix_height))

    for i in range(0, number_width * number_height, number_width):
        list_location_height.append(list_image_crop[i][1])
        print('list', i, list_image_crop[i][1])
    #
    print(len(list_location_height))
    sum_size_height = 0
    for x in list_location_height:
        sum_size_height = sum_size_height +  x[3] - x[1]
    print('\nSum', sum_size_height - overlap_height * (number_height - 1))

    x_start = 0
    y_start = 0
    count = 0
    last_img = -1

    for img in list_image_crop:
        new_image.paste(img[0], (x_start, y_start))
        pixel_total = new_image.load()
        x_start += width - overlap_width
        count = count + 1
        if count % number_width == 0:
            y_start += height - overlap_height
            x_start = 0
        if last_img != -1:
            pixel_data_2 = img[0].load()
            for i in range(x_start, x_start + overlap_width):
                if i < fix_width:
                    for j in range(y_start, y_start + overlap_height):
                        if j < fix_height:
                            if x_start > 0 and y_start > 0:
                                pixel_total[i,j] = add(pixel_total[i,j], pixel_data_2[i - x_start,j - y_start])
                            elif x_start > 0:
                                pixel_total[i,j] = add(pixel_total[i,j], pixel_data_2[i - x_start,j])
                            elif y_start > 0:
                                pixel_total[i,j] = add(pixel_total[i,j] , pixel_data_2[i,j - y_start])
        last_img = img[0]

    print("Size after merge", new_image.size)
    new_image.save(filename + '-merge.png')

def crop_save_list_image(path_image, path_save, width_crop, height_crop):
    list_img_crop = []

    for filename in os.listdir(path_image):
        image = Image.open(path_image + filename)
        filename_text = filename[0:len(filename) - 4]
        # path_save += str(filename_text)
        list_crop, size_list = crop(image, width_crop, height_crop, path_save + str(filename_text))
        list_img_crop.append(list_crop)

path_image = 'data/TissueImg/TissueImages/'
path_save = 'data/TissueImg/crop_image_512/'
width_crop = 512
height_crop = 512
# crop_save_list_image(path_image, path_save, width_crop, height_crop)


image1= Image.open(path_image + 'TCGA-18-5592-01Z-00-DX1.png')
list_crop, size_list = crop( image=image1, width_crop=300, height_crop=300, filename=None)
merge_image(list_crop, size_list, filename='TCGA-18-5592-01Z-00-DX1')