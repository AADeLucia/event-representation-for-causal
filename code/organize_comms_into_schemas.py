import jsonlines
import os
import tarfile
from tqdm import tqdm
import logging
logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    schema_folders_dir = f"{os.environ['EVENT_HOME']}/results"
    for schema_folder in tqdm(os.listdir(schema_folders_dir)):
        logging.info(f"On folder {schema_folder}")
        if "protests" in schema_folder:
            continue

        schema_folder = f"{schema_folders_dir}/{schema_folder}"
        for file in os.listdir(schema_folder):
            # Get the JSONL file with the relevant doc IDs
            if file.startswith("nyt_en_"):
                file = f"{schema_folder}/{file}"
                break

        output_folder = f"{schema_folder}/raw_comms"
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        with jsonlines.open(file) as reader:
            for obj in reader:
                filename = f"{obj['id']}.comm"
                old_path = f"{os.environ['EVENT_HOME']}/test/{filename}"
                new_path = f"{output_folder}/{filename}"
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)

        # Create tarball
        output_tarfile = f"{schema_folder}/nyt_comms.tar.gz"
        with tarfile.open(output_tarfile, "w:gz") as tar:
            tar.add(output_folder, arcname=os.path.sep)

    logging.info("Done")
