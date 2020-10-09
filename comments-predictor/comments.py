import json
# to split data into training set and test set, GridSearchCV is to tune the model
from sklearn.model_selection import train_test_split, GridSearchCV
# to use BAG OF WORDS method, Term frequency inverse document frequency Vectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn import svm  # to import the SVM classifier
# to import the Decision Tree Classifier
from sklearn.tree import DecisionTreeClassifier
# from sklearn.naive_bayes import GaussianNB  # to import the Guassian Naive Bayes Classifier
# to import the Logistic Regression Classifier
from sklearn.linear_model import LogisticRegression
# to import the F1 Score metric for classifiers
from sklearn.metrics import f1_score
# to import the K Neighbours Classifier
from sklearn.neighbors import KNeighborsClassifier
import random

# sorting the data


class Sentiment:  # class to make things more convenient
    NEGATIVE = 'NEGATIVE'
    # NEUTRAL = 'NEUTRAL'
    POSITIVE = 'POSITIVE'


class Review:  # class to make things more neat
    def __init__(self, review, rating):
        self.review = review
        self.rating = rating
        self.sentiment = self.sentiment()  # using helper function

    def review(self):
        return self.review

    def sentiment(self):
        if self.rating <= 2.5:
            # using another class to set sentiment, to avoid repeating. (called Enuming)
            return Sentiment.NEGATIVE
        else:
            return Sentiment.POSITIVE
        # elif self.rating >= 2.6:
            # return Sentiment.POSITIVE
        # else:  # score of 4 or 5
            # return Sentiment.POSITIVE

    def __str__(self):
        return '{0}\nRating: {1}\nSentiment: {2}'.format(self.review, self.rating, self.sentiment)


class ReviewContainer:
    def __init__(self, reviews):
        self.reviews = reviews

    def evenly_distribute(self):
        negative = list(filter(lambda x: x.sentiment == Sentiment.NEGATIVE,
                               self.reviews))  # filtering by sentiment
        positive = list(filter(lambda x: x.sentiment ==
                               Sentiment.POSITIVE, self.reviews))
        # shrinking the positive len to negative len
        positive_shrunk = positive[:len(negative)]
        self.reviews = negative + positive_shrunk
        random.shuffle(self.reviews)
        return self.reviews


# loading the data
reviews = []
with open('Books_small_10000.json', 'r') as file:
    for line in file:
        review = json.loads(line)  # loading each line as json dict
        # print(review['reviewText'], review['overall'])
        # appending class instances to list
        reviews.append((Review(review['reviewText'], review['overall'])))

# prepping data
# spltting data for training then testing the algorithm
training, test = train_test_split(reviews, test_size=0.25, random_state=0)


# reduced data size even after splitting
trained_container = ReviewContainer(training).evenly_distribute()
test_container = ReviewContainer(test).evenly_distribute()

# vectorizing the data
train_x = [x.review for x in trained_container]  # the data needing to be fed
train_y = [x.sentiment for x in trained_container]  # the label for the data

test_x = [x.review for x in test_container]
test_y = [x.sentiment for x in test_container]
# print(train_x[1], train_y[1])
# test_y.count(Sentiment.POSITIVE)
# test_y.count(Sentiment.NEGATIVE)

""" for this learning model we are going to use Bag of words in sklearn """

# Bag of words vectorization
# showing if words are in the review, to show word count take off binary parameter
# vectorizer = CountVectorizer()
# same as CountVectorizer but adds weightage depending on frequency to words
vectorizer = TfidfVectorizer()
# vectorizing the training review. (fitting and transfoorming the data)
train_x_vector = vectorizer.fit_transform(train_x)
# vectorizing the testing review. (only transforming it and not fitting it to the classifier)
test_x_vector = vectorizer.transform(test_x)

# print(train_x[5])
# print(train_x_vector[5])

# SVC CLASSIFIER
# Linear SVM (Support Vector Machine), (SVC = Support Vector Classifier)
clf_svm = svm.SVC(kernel='linear')
clf_svm.fit(train_x_vector, train_y)  # fitting the data in the classifier
clf_svm.predict(test_x_vector[2])  # predicting a label with the test value

# test_x[0]
# test_y[0]
# testing the classifier with the test data
test_y[0]
clf_svm.predict(test_x_vector[0])

# DECISION TREE CLASSIFIER
clf_dec = DecisionTreeClassifier()
clf_dec.fit(train_x_vector, train_y)

clf_dec.predict(test_x_vector[0])


# NAIVE BAYES CLASSFIER
# clf_gnb = GaussianNB()
# clf_gnb.fit(train_x_vector, train_y)

# LOGISTIC REGRESSION CLASSIFIER
# max_iter setting needed to stop error
clf_log = LogisticRegression(max_iter=10000)
clf_log.fit(train_x_vector, train_y)

# K NEIGHBOURS CLASSIFIER
clf_knn = KNeighborsClassifier(n_neighbors=4)  # k = 2
clf_knn.fit(train_x_vector, train_y)


# EVALUATION
# the test score for the SVM classifier (Mean accuracy)
print('SVM Classification score:', clf_svm.score(test_x_vector, test_y))
print('Decision Tree Classification score:', clf_dec.score(
    test_x_vector, test_y))  # for Decision Tree Classifier
print('Logistic Regression Classifier score:',
      clf_log.score(test_x_vector, test_y), '\n')
# F1 Scores (More important)
# to get the F1 score for the SVM Classifier
print('Positive, Negative for SVM:',
      f1_score(test_y, clf_svm.predict(test_x_vector), average=None, labels=[Sentiment.POSITIVE, Sentiment.NEGATIVE]))
# F1 score for Decision Tree
print('Positive, Negative for Decision Tree:',
      f1_score(test_y, clf_dec.predict(test_x_vector), average=None, labels=[Sentiment.POSITIVE, Sentiment.NEGATIVE]))
# F1 score for Logistic Regression
print('Positive, Negative for Logistic Regression:',
      f1_score(test_y, clf_log.predict(test_x_vector), average=None, labels=[Sentiment.POSITIVE, Sentiment.NEGATIVE]))
print('Positive, Negative for KNeighbours:',
      f1_score(test_y, clf_knn.predict(test_x_vector), average=None, labels=[Sentiment.POSITIVE, Sentiment.NEGATIVE]), '\n')


test_set = ['Shit', 'Lit', 'Fookin noice', 'Ridiculous']
new_test = vectorizer.transform(test_set)


# QUALITATIVE TESTING

print(test_set)
print('For SVM:', clf_svm.predict(new_test))
print('For Decision Tree:', clf_dec.predict(new_test))
print('For Logistic Regression:', clf_log.predict(new_test))
print('For KNeighbours:', clf_knn.predict(new_test))

# TUNING THE MODEL WITH GRID SEARCH
# what grid search does, is finds the best option of parameters for a classifier to get the best results
