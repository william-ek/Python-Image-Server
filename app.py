from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5433/bobs_burgers_images'
app.debug = False

db = SQLAlchemy(app)

class Image(db.Model):
    __tablename__ = 'image'

    id = db.Column(db.String, primary_key=True)
    savedImage = db.Column(db.LargeBinary)

    def __init__(self, image_name, image_blob):
        self.id = image_name
        self.savedImage = image_blob

    def __repr__(self):
        return '<id {}>'.format(self.id)

    @staticmethod
    def to_dict(image):
        dct = {
            "id": image.id,
            "savedImage": image.savedImage,
        }

        return dct


    @staticmethod
    def to_list_dict(images):
        return {
            "metaData": {
            },
            "items": [Image.to_dict(image) for image in images]
        }

@app.route('/image/<id>', methods=['GET'])
def getImage(id):
    try:
        result = db.session.query(Image).get(id)
        print("Results: {}".format(result))
        if result is None:
            return "record id {} is not found".format(id), 404
        return result.savedImage, 200
    except Exception as e:
        return "{}".format(e), 500

@app.route('/image', methods=['GET'])
def getOrders():
    results = Image.query.all()
    print("Results: {}".format(results))
    response = Image.to_list_dict(results)
    return results[0], 200

@app.route('/image', methods=['POST'])
def createImage():
    print("Request: {}".format(request))
    print("Body: {}".format(request.data))
    image = Image(request.args['clientFilename'], request.data)
    try:
        db.session.add(image)
        db.session.commit()
        db.session.refresh(image)
        return jsonify({'status': 'good'}), 201
    except exc.IntegrityError as i:
        print(f"Integrity: {i.orig}")
        return "{}".format(i.orig), 409
    except Exception as e:
        print("Eception: {}".format(e))
        return "{}".format(e), 500

if __name__ == '__main__':
    app.run(port=5002)