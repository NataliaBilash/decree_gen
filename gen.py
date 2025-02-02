import write
import auxil
import consts

from random import choice, randint
import argparse
from os import makedirs
import re
from time import time

from loguru import logger

def load_samples(samples_dir):
	with open(samples_dir + "/headers.txt") as headerfile:
		header = headerfile.read().split(";;\n")

	with open(samples_dir + "/names.txt") as namefile:
		name = namefile.read().split(";;\n")

	with open(samples_dir + "/intros.txt") as introfile:
		intro = introfile.read().split(";;\n")

	with open(samples_dir + "/instructions.txt") as instructionfile:
		instruction = instructionfile.read().split(";;\n")

	with open(samples_dir + "/responsible.txt") as responsiblefile:
		responsible = responsiblefile.read().split(";;\n")

	with open(samples_dir + "/creators.txt") as creatorfile:
		creator = creatorfile.read().split('\n')

	logger.info(f"[header] length: {len(header)}")
	logger.info(f"[name] length: {len(name)}")
	logger.info(f"[intro] length: {len(intro)}")
	logger.info(f"[instruction] length: {len(instruction)}")
	logger.info(f"[responsible] length: {len(responsible)}")
	logger.info(f"[creator] length: {len(creator)}")
	vars = len(header)*len(name)*len(intro)*len(instruction)
	logger.info(f"Maximum number of decrees: {vars*len(responsible)*len(creator)}")
	logger.info(f"Approximate number of different decrees: {vars}")

	return (header, name, intro, instruction, responsible, creator)

def generate(data, out, formats, size):
	logger.info(f"Using formats: {formats}")

	try:
		makedirs(out+"/json")
		if 'd' in formats:
			makedirs(out+"/docx")
		if 'p' in formats:
			makedirs(out+"/pdf")
		if 'j' in formats:
			makedirs(out+"/jpg")
	except FileExistsError:
		pass

	measure_time = 1
	count = 0
	start = time()
	while True:
		header = choice(data[0])
		name = choice(data[1])
		intro = choice(data[2])
		instruction = auxil.add_numbering(choice(data[3]))
		responsible = choice(data[4])
		creator = choice(data[5])
		date = auxil.generate_date()

		write.write_json(instruction, responsible, date, out, count)

		if 'd' in formats:
			write.write_docx(header, name, intro, instruction,
				responsible, creator, date, out, count)
		if 'p' in formats:
			write.write_pdf(header, name, intro, instruction,
				responsible, creator, date, out, count)

		if 'j' in formats:
			write.write_jpg(out, count)

		count += 1
		if count % 25 == 0:
			if auxil.getsize(out) >= size:
				logger.warning(f"Size of {out} dir: {auxil.getsize(out)} bytes")
				break

		if measure_time:
			if count % 100 == 0:
				avg_speed = auxil.getsize(out) / (time()-start)
				full_time = round((size) / (avg_speed*60), 2)
				measure_time = 0
				if full_time < 1:
					logger.warning("Approximate generation time: "
								  f"{round(full_time*60, 2)} s.")
				else:
					logger.warning("Approximate generation time: "
								  f"{full_time} min.")


def get_args():
	parser = argparse.ArgumentParser(
		description="Decrees generator",
		epilog="Example: python3 gen.py 50MB -f dp -s samples -o decrees -vv")

	parser.add_argument("size", help="Max size of output dir. For example: 10KB, 10MB, 10GB",
						type=auxil.check_size_format)
	parser.add_argument("-f", "--format", help="Formats to save (docx: d, pdf: p, jpg: j)",
						type=auxil.parse_formats, default="d", metavar="format")
	parser.add_argument("-s", "--samples", help="Path to dir with samples",
						metavar="path", type=str, default="./samples/")
	parser.add_argument("-o", "--out", help="Path for output files",
						metavar="path", type=str, default="./decrees")
	parser.add_argument("-v", "--verbose", action="count", default=0)

	return parser.parse_args()

def main():
	args = get_args()
	auxil.logger_config(args.verbose)

	data = load_samples(args.samples)
	bytes_size = auxil.size_to_bytes(args.size)

	generate(data, args.out, args.format, bytes_size)

	logger.warning("Generation is finished!")

if __name__ == '__main__':
	main()
