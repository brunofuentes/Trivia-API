import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  #Cors to allow '*' for origins.
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
  endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
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
  endpoint to handle GET requests for all available categories.
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
  endpoint to get questions based on category. 
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
          'total_questions': len(Question.query.filter(Question.category == category_id).all()),
          'current_category': category_id
        })
    except BaseException:
      abort(422) #not able to process request

  '''
  endpoint to DELETE question using a question ID. 
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
  endpoint to POST a new question, 
  '''

  @app.route('/questions/add', methods=['POST'])
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
  endpoint to get questions based on a search term. 
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
  endpoint to get questions to play the quiz. 
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
  Error handlers for all expected errors
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
      'message': 'Unprocessable'
    }), 422

  @app.errorhandler(500)
  def server_error(error):

    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal server error'
    }), 500
  
  return app

    