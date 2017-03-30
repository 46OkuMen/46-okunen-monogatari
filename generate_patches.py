import os
import shutil
from rominfo import files, disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images
from utils import SRC_ROM_PATH, TYPESET_ROM_PATH, SRC_PATH, TYPESET_PATH
from romtools.disk import Disk
from romtools.patch import Patch

EVODiskAOriginal = Disk(SRC_ROM_PATH)
EVODiskAEdited = Disk(TYPESET_ROM_PATH)

for f in files:
    print f
    EVODiskAEdited.extract(f, dest_path='.')
    shutil.copyfile(f, 'edited_' + f)
    EVODiskAOriginal.extract(f, dest_path='.')

    patch_filename = f + '.xdelta'
    patch_destination = os.path.join('patch', patch_filename)
    filepatch = Patch(f, patch_destination, edited='edited_' + f)
    filepatch.create()
    os.remove(f)
    os.remove('edited_' + f)

# TODO: Generate the 46.EXE patches for the HDI and HDM versions, too.
disk_enum = ['46 Okunen Monogatari - The Sinkaron (J) A user.FDI',
                '46 Okunen Monogatari - The Sinkaron (J) B 2.FDI',
                '46 Okunen Monogatari - The Sinkaron (J) B 3.FDI',
                '46 Okunen Monogatari - The Sinkaron (J) B 4.FDI']
for i, disk in enumerate([disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images]):
    ImgDisk = Disk(disk_enum[i])
    print ImgDisk
    for img in disk:
        original_file = os.path.join('original_roms', 'gdt', img)
        edited_file = os.path.join('typeset_roms', 'gdt', img)
        patch_filename = os.path.join('patch', img + '.xdelta')
        imagepatch = Patch(original_file, patch_filename, edited=edited_file)
        imagepatch.create()

d88_images = ['46okumus.D88', '46okumd1.D88', '46okumd2.D88', '46okumd3.D88', '46okumsy.D88']

for d in d88_images:
    original = os.path.join(SRC_PATH, d)
    patched = os.path.join(TYPESET_PATH, d)

    patch_filename = os.path.join('patch', d + '.xdelta')
    D88Patch = Patch(original, patched, patch_filename)
    D88Patch.create()