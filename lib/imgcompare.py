# MIT License
#
# Copyright (c) 2016 Jonas Hahn <jonas.hahn@datenhahn.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from PIL import Image
from PIL import ImageChops

"""
  === imagecompare ===

  This little tool compares two images using pillow's ImageChops and then converts the differnce to
  black/white and sums up all found differences by summing up the histogram values of the difference
  pixels.

  Taking the difference between a black and a white image of the same size as base a percentage value
  is calculated.

  Check the tests to see example diffs for different scenarios. Don't expect the diff of two jpg images be
  the same for the same images converted to png. Don't do interformat compares (e.g. JPG with PNG).

  Usage:

  == compare images ==

    same = is_equal("image_a.jpg", "image_b.jpg")

    # use the tolerance parameter to allow a certain diff pass as same
    same = is_equal("image_a.jpg", "image_b.jpg", tolerance=2.5)

  == get the diff percentage ==

    percentage = image_diff_percent("image_a.jpg", "image_b.jpg")

    # or work directly with pillow image instances
    image_a = Image.open("image_a.jpg")
    image_b = Image.open("image_b.jpg")
    percentage = image_diff_percent(image_a, image_b)

"""


class ImageCompareException(Exception):
    """
    Custom Exception class for imagecompare's exceptions.
    """
    pass


def pixel_diff(image_a, image_b):
    """
    Calculates a black/white image containing all differences between the two input images.

    :param image_a: input image A
    :param image_b: input image B
    :return: a black/white image containing the differences between A and B
    """

    if image_a.size != image_b.size:
        raise ImageCompareException(
            "different image sizes, can only compare same size images: A=" + str(image_a.size) + " B=" + str(
                image_b.size))

    if image_a.mode != image_b.mode:
        raise ImageCompareException(
            "different image mode, can only compare same mode images: A=" + str(image_a.mode) + " B=" + str(
                image_b.mode))

    diff = ImageChops.difference(image_a, image_b)
    diff = diff.convert('L')

    return diff


def total_histogram_diff(pixel_diff):
    """
    Sums up all histogram values of an image. When used with the black/white pixel-diff image
    this gives the difference "score" of an image.

    :param pixel_diff: the black/white image containing all differences (output of imagecompare.pixel_diff function)
    :return: the total "score" of histogram values (histogram values of found differences)
    """
    return sum(i * n for i, n in enumerate(pixel_diff.histogram()))


def image_diff(image_a, image_b):
    """
    Calculates the total difference "score" of two images. (see imagecompare.total_histogram_diff).

    :param image_a: input image A
    :param image_b: input image A
    :return: the total difference "score" between two images
    """
    histogram_diff = total_histogram_diff(pixel_diff(image_a, image_b))

    return histogram_diff


def is_equal(image_a, image_b, tolerance=0.0):
    """
    Compares two image for equalness. By specifying a tolerance a certain diff can
    be allowed to pass as True.

    :param image_a: input image A
    :param image_b: input image B
    :param tolerance: allow up to (including) a certain percentage of diff pass as True
    :return: True if the images are the same, false if they differ
    """
    return image_diff_percent(image_a, image_b) <= tolerance


def image_diff_percent(image_a, image_b):
    """
    Calculate the difference between two images in percent.

    :param image_a: input image A
    :param image_b: input image B
    :return: the difference between the images A and B as percentage
    """

    # if paths instead of image instances where passed in
    # load the images
    if isinstance(image_a, str):
        image_a = Image.open(image_a)

    if isinstance(image_b, str):
        image_b = Image.open(image_b)

    # first determine difference of input images
    input_images_histogram_diff = image_diff(image_a, image_b)

    # to get the worst possible difference use a black and a white image
    # of the same size and diff them

    black_reference_image = Image.new('RGB', image_a.size, (0, 0, 0))
    white_reference_image = Image.new('RGB', image_a.size, (255, 255, 255))

    worst_bw_diff = image_diff(black_reference_image, white_reference_image)

    percentage_histogram_diff = (input_images_histogram_diff / float(worst_bw_diff)) * 100

    return percentage_histogram_diff
