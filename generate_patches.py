import os
import shutil
from rominfo import files, disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images
from utils import SRC_ROM_PATH, TYPESET_ROM_PATH
from romtools.disk import Disk
from romtools.patch import Patch

EVODiskAOriginal = Disk(SRC_ROM_PATH)
EVODiskAEdited = Disk(TYPESET_ROM_PATH)

for f in files:
    EVODiskAEdited.extract(f)
    shutil.copyfile(f, 'edited_' + f)
    EVODiskAOriginal.extract(f)

    patch_filename = f + '.xdelta'
    patch_destination = os.path.join('patch', patch_filename)
    filepatch = Patch(f, 'edited_' + f, patch_destination)
    filepatch.create()
    os.remove(f)
    os.remove('edited_' + f)

# TODO: Generate the 46.EXE patches for the HDI and HDM versions, too.
list_to_disk = ['46 Okunen Monogatari - The Sinkaron (J) A user.FDI',
                '46 Okunen Monogatari - The Sinkaron (J) B 2.FDI',
                '46 Okunen Monogatari - The Sinkaron (J) B 3.FDI',
                '46 Okunen Monogatari - The Sinkaron (J) B 4.FDI']
for i, disk in enumerate([disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images]):
    ImgDisk = Disk(list_to_disk[i])
    print ImgDisk
    for img in disk:
        original_file = os.path.join('original_roms', 'gdt', img)
        edited_file = os.path.join('typeset_roms', 'gdt', img)
        patch_filename = os.path.join('patch', img + '.xdelta')
        imagepatch = Patch(original_file, edited_file, patch_filename)
        imagepatch.create()