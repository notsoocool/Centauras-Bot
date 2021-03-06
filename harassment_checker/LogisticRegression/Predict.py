import pickle
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import spacy

spacy.load("en_core_web_sm")
lemmatizer = spacy.lang.en.English()

def token(data):
    tokens = lemmatizer(data)
    return [token.lemma_ for token in tokens]

def predict(text):
    with open('E:/WEB_DEVELOPMENT/selenium/centauras_bot/harassment_checker/LogisticRegression/model_saved/TFIDF.pkl', 'rb') as file:  
        Pickled_LR_Model = pickle.load(file)
    vectorizer = TfidfVectorizer(tokenizer=token, ngram_range=(1,2), stop_words='english')
    X_test = vectorizer.fit_transform(text)
    y_predicted = Pickled_LR_Model.predict(X_test)
    return y_predicted

