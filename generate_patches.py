import os
import shutil
from rominfo import files, disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images
from utils import SRC_ROM_PATH, TYPESET_ROM_PATH, SRC_PATH, TYPESET_PATH, ORIGINAL_PATH
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

# sets: FDI, d88, NK HDM, NK HDI
set_dirs = ['', 'd88', 'NeoKobe', 'NeoKobe']

sets = (['46 Okunen Monogatari - The Sinkaron (J) A user.FDI', '46 Okunen Monogatari - The Sinkaron (J) B 2.FDI',
         '46 Okunen Monogatari - The Sinkaron (J) B 3.FDI', '46 Okunen Monogatari - The Sinkaron (J) B 4.FDI'],
        ['46okumus.D88', '46okumd1.D88', '46okumd2.D88', '46okumd3.D88'],
        ['46 Okunen Monogatari - The Shinkaron (Disk 1 - User disk).hdm', '46 Okunen Monogatari - The Shinkaron (Disk 2).hdm',
        '46 Okunen Monogatari - The Shinkaron (Disk 3).hdm', '46 Okunen Monogatari - The Shinkaron (Disk 4).hdm'],
        ['46 Okunen Monogatari - The Shinkaron.hdi',],
       )

for i, s in enumerate(sets):
    set_original_dir = os.path.join(ORIGINAL_PATH, set_dirs[i])
    set_patched_dir = os.path.join(TYPESET_PATH, set_dirs[i])
    for disk in s:
        original = os.path.join(set_original_dir, disk)
        patched = os.path.join(set_patched_dir, disk)
        print original
        print patched

        patch_filename = os.path.join('patch', disk + '.xdelta')
        FullDiskPatch = Patch(original, patch_filename, edited=patched)
        FullDiskPatch.create()

floppy_46_path = os.path.join(ORIGINAL_PATH, '46.EXE')
hacked_and_patched_46_path = os.path.join(TYPESET_PATH, 'HDI_patched_46', '46.EXE')
print floppy_46_path
print hacked_and_patched_46_path
FtoH_46_patch_path = os.path.join('patch', 'FtoH_46.EXE' + '.xdelta')
FtoH46Patch = Patch(floppy_46_path, FtoH_46_patch_path, edited=hacked_and_patched_46_path)
FtoH46Patch.create()