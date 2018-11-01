for N in {1..4}; do \
python ./facenet/src/align/align_dataset_mtcnn.py \
./data_test \
./data_test_mtcnnpy_160 \
--image_size 160 \
--margin 32 \
--random_order \
--gpu_memory_fraction 0.25 \
& done



# To  Validate
python ./facenet/src/validate_on_lfw.py \
./data_mtcnnpy_160 \
./facenet/models/20180402-114759 \
--distance_metric 1 \
--use_flipped_images \
--subtract_mean \
--use_fixed_image_standardization


# To Train
python ./facenet/src/classifier.py TRAIN ./data_v2_mtcnnpy_160 \
/home/snow/Desktop/Face-Tag/models/20180402-114759.pb \
/home/snow/Desktop/Face-Tag/models/ft_v2__classifier.pkl \
--batch_size 1000 --min_nrof_images_per_class 40 \
--nrof_train_images_per_class 35 --use_split_dataset

# To Classify
python ./facenet/src/classifier.py CLASSIFY ./data_mtcnnpy_160 \
/home/snow/Desktop/Face-Tag/models/20180402-114759.pb \
/home/snow/Desktop/Face-Tag/models/ft_v1__classifier.pkl \
--batch_size 1000 --min_nrof_images_per_class 40 \
--nrof_train_images_per_class 35 --use_split_dataset



python ./facenet/src/validate_on_lfw.py \
./data_mtcnnpy_160 \
./20180402-114759 \
--distance_metric 1 \
--use_flipped_images \
--subtract_mean \
--use_fixed_image_standardization
