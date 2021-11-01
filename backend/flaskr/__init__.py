import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE      # Each page will show 10 questions
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  #Cors to allow '*' for origins. TODO: Deleve the sample route after completing the TODOs.
  CORS(app, resources=r'/api/*')

  #CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add(
      "Access-Control-Allow-Headers", 
      "Content-Type, Authorization, true")

    response.headers.add(
      "Access-Control-Allow-Methods",
      "GET,PUT,POST,DELETE,OPTIONS")

    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions', methods=['GET'])
  def retrieve_questions():

    selection = Question.query.order_by(Question.id)
    all_categories = list(map(Category.format, Category.query.all()))
    current_questions = paginate_questions(request, selection)

    if len(current_questions) == 0:
      abort(404)
    
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'current category': None,
      'categories': all_categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories', methods=['GET'])
  def retrive_categories():
    all_categories = list(map(Category.format, Category.query.all()))

    if len(all_categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': all_categories,
      'total_categories': len(all_categories)
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions')
  def retrieve_questions_by_category(category_id):

    try:
      questions_by_category = Question.query.order_by(Question.id).filter(
        Question.category == category_id).all()
      questions_paginated = paginate_questions(request, questions_by_category)

      if len(questions_paginated) == 0:
        abort(404)

      else:
        return jsonify({
          'success': True,
          'questions': questions_paginated,
          'total_questions': len(Question.query.all()),
          'current category': category_id
        })
    except BaseException:
      abort(422) #not able to process request

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):

    try:

      question = Question.query.filter(
        Question.id == question_id).one_or_none()

      if question is None:
        abort(404)
      
      else:
        question.delete()

      return jsonify({
        'success': True,
        'deleted': question.format(),
        'deleted_id': question_id,
      })

    except BaseException:
      abort(422)  #not able to process request

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def new_question():
    
    body = request.get_json()
    question = body.get('question', None)
    answer = body.get('answer', None)
    category = body.get('category', None)
    difficulty = body.get('difficulty', None)

    try:
      question = Question(
        question = question,
        answer = answer,
        category = category,
        difficulty = difficulty
      )

      question.insert()

      return jsonify({
        'success': True,
        'created': question.id
      })
    except BaseException:
      abort(422) #not able to process request
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/search', methods=['POST'])
  def search_question():

    body = request.get_json()
    search = body.get('searchTerm', None)

    questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))

    questions_paginated = paginate_questions(request, questions)

    return jsonify({
      'success': True,
      'questions': questions_paginated
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def retrieve_quizzes():

    #get RAW data
    questions = None
    body = request.get_json()
    quiz_category = body.get('quiz_category', None)
    previous_questions = body.get('previous_questions', None)
    category_id = quiz_category['id']

    try:

      #check category
      if category_id == 0:
        questions = Question.query.all()
      else:
        category_id = quiz_category['id']
        questions = Question.query.filter(Question.category == category_id).all()
      
      new_questions = []

      for question in questions:
        if question.id not in previous_questions:
          new_questions.append(question)

      if new_questions== []:
        formatted_question = 0

      else:
        #get a random question from database.
        question = random.choice(questions)
        formatted_question = question.format()
        previous_questions.append(question)

        return jsonify({
          'success': True,
          'question': formatted_question
        })    
    except BaseException:
      abort(404) #not found


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):

    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad Request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):

    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Not Found'
    }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):

    return jsonify({
      'success': False,
      'error': 405,
      'message': 'Method not allowed'
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):

    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable'
    }), 422

  @app.errorhandler(500)
  def server_error(error):

    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal server error'
    }), 500
  
  return app

    