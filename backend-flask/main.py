from flask import Flask, request, send_file, Response, jsonify
from flask_cors import CORS
import base64
import json
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
filename = 'train.csv'

class TrainResult(db.Model):
    __tablename__ = 'train_result'
    id = db.Column(db.Integer, primary_key=True)
    dataset = db.Column(db.String(200))
    epoch = db.Column(db.Integer)
    lr = db.Column(db.Float)
    elasticNetParam = db.Column(db.Float)
    accuracy = db.Column(db.Float)

    def __init__(self, dataset, epoch, lr, elasticNetParam, accuracy):
        self.dataset = dataset
        self.epoch = epoch
        self.lr = lr
        self.elasticNetParam = elasticNetParam
        self.accuracy = accuracy

# for debugging show all users
@app.route('/debug')
def show_table():
    users = TrainResult.query.all()
    message = []
    for user in users:
        user_data = {}
        user_data['dataset'] = user.dataset
        user_data['epoch'] = user.epoch
        user_data['lr'] = user.lr
        user_data['elasticNetParam'] = user.elasticNetParam
        user_data['accuracy'] = user.accuracy
        message.append(user_data)
    return jsonify({'users':message})

@app.route('/', methods=['POST'])
def index():
    """
    POST route handler that accepts an image, manipulates it and returns a JSON containing a possibly different image with more fields
    """
    # Read image from request and write to server's file system
    # print(request.files)
    data = request.files['file'] 
    # data.save('save_pic.jpg')
    data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  
    # Do something with the image e.g. transform, crop, scale, computer vision detection
    # some_function_you_want()

    # Return the original/manipulated image with more optional data as JSON
    # saved_img = open('save_pic.jpg', 'rb').read() # Read as binary
    # saved_img_b64 = base64.b64encode(saved_img).decode('utf-8') # UTF-8 can be converted to JSON
    # response = {}
    # response['data'] = saved_img_b64
    # response['more_fields'] = 'more data' # Can return values such as Machine Learning accuracy or precision
    params = {
            'epoch': request.values['epoch'],
            'lr': request.values['lr'],
            'elasticNetParam': request.values['elasticNetParam']
        }
        # Train here

    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName('ml-diabetes').master('local').getOrCreate()
    df = spark.read.csv(os.path.join(app.config['UPLOAD_FOLDER'], filename), header = True, inferSchema = True)
    # df.printSchema()

    import pandas as pd
    # pd.DataFrame(df.take(5), columns=df.columns).transpose()

    # df.show()
    # df.toPandas()

    # df.groupby('Outcome').count().toPandas()

    numeric_features = [t[0] for t in df.dtypes if t[1] == 'int']
    # df.select(numeric_features).describe().toPandas().transpose()

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from pandas.plotting import scatter_matrix
    numeric_data = df.select(numeric_features).toPandas()

    axs = scatter_matrix(numeric_data, figsize=(8, 8))

    # Rotate axis labels and remove axis ticks
    n = len(numeric_data.columns)
    for i in range(n):
        v = axs[i, 0]
        v.yaxis.label.set_rotation(0)
        v.yaxis.label.set_ha('right')
        v.set_yticks(())
        h = axs[n-1, i]
        h.xaxis.label.set_rotation(90)
        h.set_xticks(())

    plt.savefig('static/figure_1.jpg')
    plt.close('all')

    from pyspark.sql.functions import isnull, when, count, col

    # df.select([count(when(isnull(c), c)).alias(c) for c in df.columns]).show()

    dataset = df
    # dataset = dataset.drop('SkinThickness')
    # dataset = dataset.drop('Insulin')
    # dataset = dataset.drop('DiabetesPedigreeFunction')
    # dataset = dataset.drop('Pregnancies')

    # dataset.show()

    # Assemble all the features with VectorAssembler
    # required_features = ['Glucose',
    #                     'BloodPressure',
    #                     'BMI',
    #                     'Age'
    #                 ]

    from pyspark.ml.feature import VectorAssembler

    print(dataset.columns[:-1])
    assembler = VectorAssembler(inputCols=dataset.columns[:-1], outputCol='features')

    transformed_data = assembler.transform(dataset)
    transformed_data.show()

    # Split the data
    (training_data, test_data) = transformed_data.randomSplit([0.8,0.2], seed =2020)
    print("Training Dataset Count: " + str(training_data.count()))
    print("Test Dataset Count: " + str(test_data.count()))

    from pyspark.ml.classification import LogisticRegression

    print(int(params['epoch']))
    print(float(params['lr']))
    print(float(params['elasticNetParam']))
    lr = LogisticRegression(featuresCol = 'features', labelCol = 'Outcome', maxIter=int(params['epoch']), regParam=float(params['lr']), elasticNetParam=float(params['elasticNetParam']))
    lrModel = lr.fit(training_data)
    lr_predictions = lrModel.transform(test_data)

    from pyspark.ml.evaluation import MulticlassClassificationEvaluator

    multi_evaluator = MulticlassClassificationEvaluator(labelCol = 'Outcome', metricName = 'accuracy')
    print('Logistic Regression Accuracy:', multi_evaluator.evaluate(lr_predictions))


    trainingSummary = lrModel.summary
    objectiveHistory = trainingSummary.objectiveHistory
    print("objectiveHistory:")
    for objective in objectiveHistory:
        print(objective)

    plt.plot(objectiveHistory)
    plt.ylabel('training loss')
    plt.xticks(range(len(objectiveHistory)))
    plt.savefig('static/figure_2.jpg')
    plt.close('all')

    # session['result']= "Training Loss=%.3f Acc=%.2f" % (objectiveHistory[-1], multi_evaluator.evaluate(lr_predictions))
    # session['complete'] = True

    # resp = make_response(redirect('/'))
    # resp.set_cookie('epoch', request.form['epoch'])
    # resp.set_cookie('lr', request.form['lr'])
    # resp.set_cookie('elasticNetParam', request.form['elasticNetParam'])
    # If only the image is required, you can use send_file instead
    # return send_file('save_pic.jpg', mimetype='image/jpg')
    result = {
        "loss": objectiveHistory[-1], 
        "acc": multi_evaluator.evaluate(lr_predictions)
    } 
    # return Response(json.dumps(result))

    saved_img = open('static/figure_2.jpg', 'rb').read() # Read as binary
    saved_img_b64 = base64.b64encode(saved_img).decode('utf-8') # UTF-8 can be converted to JSON
    response = {}
    response['fig2'] = saved_img_b64
    saved_img = open('static/figure_1.jpg', 'rb').read() # Read as binary
    saved_img_b64 = base64.b64encode(saved_img).decode('utf-8') # UTF-8 can be converted to JSON
    response['fig1'] = saved_img_b64
    response['loss'] = objectiveHistory[-1] # Can return values such as Machine Learning accuracy or precision
    response['acc'] = multi_evaluator.evaluate(lr_predictions)

    data = TrainResult(filename, int(params['epoch']), float(params['lr']), float(params['elasticNetParam']), response['acc'])
    db.session.add(data)
    db.session.commit()
    return Response(json.dumps(response))
    # return Response(json.dumps(response)

@app.route("/get-image/<image_name>")
def get_image(image_name):

    try:
        saved_img = open(image_name + '.jpg', 'rb').read() # Read as binary
        saved_img_b64 = base64.b64encode(saved_img).decode('utf-8') # UTF-8 can be converted to JSON
        response = {}
        response['data'] = saved_img_b64
        response['more_fields'] = 'more data' # Can return values such as Machine Learning accuracy or precision
        return Response(json.dumps(response))
        # return send_file('static/' + image_name + '.jpg', mimetype='image/jpg')
    except FileNotFoundError:
        abort(404)