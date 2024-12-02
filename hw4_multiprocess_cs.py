from docx import Document
from pathlib import Path
from multiprocessing import Barrier, Queue, Process
import logging
import time


keyWords = ['apple', 'sunflower', 'robotics', 'Python', 'ocean', 'mountain', 'harmony', 'adventure', 'future', 'discovery']
folder_paths = ['./source/first_group',
                './source/second_group', './source/third_group']




def findKeyWord(folder_path, keyWords, barrier, results_queue, wait_time_tracker):
    process_wait_time = 0

    results = []
    for keyWord in keyWords:
        #logging.debug(f'Process is ready to work on folder: {folder_path}, keyword: {keyWord}')

        start_wait_time = time.time()
        barrier.wait()
        end_wait_time = time.time()
        wait_duration = end_wait_time - start_wait_time
        process_wait_time += wait_duration
        #logging.debug(f"Waiting at barrier took {wait_duration:.4f} seconds for folder: {folder_path}, keyword: {keyWord}")

        #logging.debug(f"Process's just started working on folder: {folder_path}, keyword: {keyWord}")

        files_read = Path(folder_path)

        for file in files_read.iterdir():
            if file.suffix == '.docx':
                try:
                    doc = Document(file)
                    for paragraph in doc.paragraphs:
                        if keyWord in paragraph.text:
                            results.append({'keyWord': keyWord,'path': str(file)})
                            break
                except Exception as e:
                    logging.error(f"There is the mistake {file}:{e}")

    results_queue.put(results)
    wait_time_tracker.put(process_wait_time)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,format='%(processName)s: %(message)s')
    processes = []
    results_queue = Queue()
    wait_time_tracker = Queue() 
    barrier = Barrier(len(folder_paths))
    final_results = []


    for folder_path in folder_paths:
        process = Process(target=findKeyWord, args=(folder_path, keyWords, barrier, results_queue, wait_time_tracker))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()


    while not results_queue.empty():
        final_results.extend(results_queue.get())


    total_wait_time = 0
    while not wait_time_tracker.empty():
        total_wait_time += wait_time_tracker.get()


    logging.info("Final dictionary with results:")
    for entry in final_results:
        logging.info(entry)

    logging.info(f"Total waiting time across all processes: {
                 total_wait_time:.4f} seconds")
