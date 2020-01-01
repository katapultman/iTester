from database import DB
from question import Question
from typing import List
from adapter import Adapter

class Test:
	def __init__(self, id: int, questions: List[Question], title: str):
		self.title = title
		self.questions = questions
		self.id = id
		self.correct_answers = [False for _ in range(len(questions))] # create a 'False' boolean list w/list comprehension
	
	def check_test(self):
		for question in self.questions:
			self.correct_answers[self.questions.index(question)] = "Correct" if question.is_answer_correct() else "Incorrect"
			# set whether current question is correct
	
	def set_answers(self, answers: List[str]): # answer amount should be identical to question amount
		if len(answers) != len(self.questions):
			return False
			
		for question in self.questions:
			question.set_answer(answers[self.questions.index(question)]) 
			# set answer of question to one given (will be garnered through requests and made into list)
			
	def count_correct(self):
		return (self.correct_answers.count("Correct") / len(self.correct_answers)) * 100
		
	def count_incorrect(self):
		return (self.correct_answers.count("Incorrect") / len(self.correct_answers)) * 100

	def create(self):
		with DB() as database:
			database.execute('''
				INSERT INTO tests (id, questions_id, title)
				VALUES (?, ?, ?)''', (self.id, self.id, self.title))
			
					
			for question in self.questions: # int array of question ids to categorise test questions by
				database.execute('''
				INSERT INTO test_questions (test_id, question_id) VALUES (?, ?)
				''', (self.id, question.id))
				
			return self

	@staticmethod
	def get_all():
		with DB() as database:
			rows = database.execute('''SELECT * FROM tests''').fetchall() # fetches all rows which correspond to the query (i.e. every row)

			rows = Adapter.adapt_test_rows(database, Adapter.adapt_query(rows), Question.get_test_questions(
				database.execute('''
				SELECT question_id FROM test_questions
				''').fetchall())) 
			# new rows is result of adapted method return value 
			# adapt query converts list of tuples into list of lists
			
			return [Test(*row) for row in rows] 
			# for each row in the data, instantiate a class with the values from the table
			# and return them all as a list

	@staticmethod
	def find(id):
		with DB() as database:
			row = Adapter.adapt_query(database.execute('''SELECT * FROM tests WHERE id = ?''', (id,)).fetchall())
			# rather banal back-and-forth type conversion from list of tuples to list of lists
			
			question_order = database.execute('''
				SELECT question_id FROM test_questions
				''').fetchall()
				
							
			question_order = [question_order[question_id:question_id+3] for question_id in range(0, len(question_order), 3)] # create list of lists spliced by 3
			
			print(question_order)
			
			row = tuple(Adapter.adapt_test_rows(database, row, Question.get_test_questions(question_order[id - 1]))[0])
			
			print(row)
			
			# fetch a single row where id is given id
			# sql queries take tuples, which is why we pass arguments in such a manner
			
			return Test(*row) # return new instance of Test() where we pass the elements of the container as args
