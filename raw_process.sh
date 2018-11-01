for N in {1..4}; do \
/home/snow/.virtualenvs/FACE-TAG/bin/python ~/Desktop/Face-Tag/facenet/src/align/align_dataset_mtcnn.py \
./data/ \
./data_mtcnnpy_160 \
--image_size 160 \
--margin 32 \
--random_order \
--gpu_memory_fraction 0.25 \
& done
