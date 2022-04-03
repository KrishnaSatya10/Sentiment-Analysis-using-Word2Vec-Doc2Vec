from turtle import pos
from xml.sax.handler import all_properties
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import time
from numpy import zeros, empty, isnan, random, uint32, float32 as REAL, vstack
import sys
import collections
#from gensim_models.doc2vec_modified import LabeledSentence
import sklearn.naive_bayes
import sklearn.linear_model
import nltk
import random
import _pickle as pickle
from collections import defaultdict
random.seed(0)
nltk.download("stopwords")          # Download the stop words from nltk
#from gensim.models.deprecated.doc2vec import TaggedDocument
#from gensim_models import word2vec
#from gensim_models import doc2vec_modified
#from gensim_models.doc2vec_modified import TaggedDocument, Doc2Vec

# User input path to the train-pos.txt, train-neg.txt, test-pos.txt, and test-neg.txt datasets
if len(sys.argv) != 3:
    print("python sentiment.py <path_to_data> <nlp|d2v|w2v>")
    exit(1)
path_to_data = sys.argv[1]
method = sys.argv[2]

if method == "w2v":
    path_to_pretrained_w2v = ""


def main():
    train_pos, train_neg, test_pos, test_neg = load_data(path_to_data)

    # Using saved models and vectors for method == 'nlp'. (Orginal runtime = 5 mins; Current runtime = 10 seconds)
    if method == "nlp":
        train_pos_vec, train_neg_vec, test_pos_vec, test_neg_vec = feature_vecs_NLP(
            train_pos, train_neg, test_pos, test_neg)
        filename = './'+path_to_data+'train_pos_vec_nlp.txt'
        pickle.dump(train_pos_vec, open(filename, 'wb'))
        train_pos_vec = pickle.load(open(filename, 'rb'))
        filename = './'+path_to_data+'train_neg_vec_nlp.txt'
        pickle.dump(train_neg_vec, open(filename, 'wb'))
        train_neg_vec = pickle.load(open(filename, 'rb'))
        filename = './'+path_to_data+'test_pos_vec_nlp.txt'
        pickle.dump(test_pos_vec, open(filename, 'wb'))
        test_pos_vec = pickle.load(open(filename, 'rb'))
        filename = './'+path_to_data+'test_neg_vec_nlp.txt'
        pickle.dump(test_neg_vec, open(filename, 'wb'))
        test_neg_vec = pickle.load(open(filename, 'rb'))

        nb_model, lr_model = build_models_NLP(train_pos_vec, train_neg_vec)
        filename = './'+path_to_data+'nb_model_nlp.sav'
        pickle.dump(nb_model, open(filename, 'wb'))
        nb_model = pickle.load(open(filename, 'rb'))
        filename = './'+path_to_data+'lr_model_nlp.sav'
        pickle.dump(lr_model, open(filename, 'wb'))
        lr_model = pickle.load(open(filename, 'rb'))

    # Using saved models and vectors for method == 'd2v'. (Orginal runtime = 10 mins; Current runtime = 10 seconds)
    if method == "d2v":
        train_pos_vec, train_neg_vec, test_pos_vec, test_neg_vec = feature_vecs_DOC(
            train_pos, train_neg, test_pos, test_neg)
        filename = './'+path_to_data+'train_pos_vec_d2v.txt'
        pickle.dump(train_pos_vec, open(filename, 'wb'))
        train_pos_vec = pickle.load(open(filename, 'rb'))
        filename = './'+path_to_data+'train_neg_vec_d2v.txt'
        pickle.dump(train_neg_vec, open(filename, 'wb'))
        train_neg_vec = pickle.load(open(filename, 'rb'))
        filename = './'+path_to_data+'test_pos_vec_d2v.txt'
        pickle.dump(test_pos_vec, open(filename, 'wb'))
        test_pos_vec = pickle.load(open(filename, 'rb'))
        filename = './'+path_to_data+'test_neg_vec_d2v.txt'
        pickle.dump(test_neg_vec, open(filename, 'wb'))
        test_neg_vec = pickle.load(open(filename, 'rb'))

        nb_model, lr_model = build_models_DOC(train_pos_vec, train_neg_vec)
        filename = './'+path_to_data+'nb_model_d2v.sav'
        pickle.dump(nb_model, open(filename, 'wb'))
        nb_model = pickle.load(open(filename, 'rb'))
        filename = './'+path_to_data+'lr_model_d2v.sav'
        pickle.dump(lr_model, open(filename, 'wb'))
        lr_model = pickle.load(open(filename, 'rb'))

    if method == "w2v":
        train_pos_vec, train_neg_vec, test_pos_vec, test_neg_vec = feature_vecs_DOC_W2V(
            train_pos, train_neg, test_pos, test_neg)
        filename = './'+path_to_data+'train_pos_vec_w2v.txt'
        pickle.dump(train_pos_vec, open(filename, 'wb'))
        train_pos_vec = pickle.load(open(filename, 'rb'))
        filename = './'+path_to_data+'train_neg_vec_w2v.txt'
        pickle.dump(train_neg_vec, open(filename, 'wb'))
        train_neg_vec = pickle.load(open(filename, 'rb'))
        filename = './'+path_to_data+'test_pos_vec_w2v.txt'
        pickle.dump(test_pos_vec, open(filename, 'wb'))
        test_pos_vec = pickle.load(open(filename, 'rb'))
        filename = './'+path_to_data+'test_neg_vec_w2v.txt'
        pickle.dump(test_neg_vec, open(filename, 'wb'))
        test_neg_vec = pickle.load(open(filename, 'rb'))

        nb_model, lr_model = build_models_DOC_W2V(train_pos_vec, train_neg_vec)
        filename = './'+path_to_data+'nb_model_w2v.sav'
        pickle.dump(nb_model, open(filename, 'wb'))
        filename = './'+path_to_data+'lr_model_w2v.sav'
        pickle.dump(lr_model, open(filename, 'wb'))

    print("Naive Bayes")
    print("-----------")
    evaluate_model(nb_model, test_pos_vec, test_neg_vec, True)

    print("")
    print("Logistic Regression")
    print("-------------------")
    evaluate_model(lr_model, test_pos_vec, test_neg_vec, True)


def load_data(path_to_dir):
    """
    Loads the train and test set into four different lists.
    """
    train_pos = []
    train_neg = []
    test_pos = []
    test_neg = []
    with open(path_to_dir+"train-pos.txt", "r") as f:
        for i, line in enumerate(f):
            words = [w.lower() for w in line.strip().split() if len(w) >= 3]
            if (len(words) == 0):
                continue
            train_pos.append(words)
    with open(path_to_dir+"train-neg.txt", "r") as f:
        for line in f:
            words = [w.lower() for w in line.strip().split() if len(w) >= 3]
            if (len(words) == 0):
                continue
            train_neg.append(words)
    with open(path_to_dir+"test-pos.txt", "r") as f:
        for line in f:
            words = [w.lower() for w in line.strip().split() if len(w) >= 3]
            if (len(words) == 0):
                continue
            test_pos.append(words)
    with open(path_to_dir+"test-neg.txt", "r") as f:
        for line in f:
            words = [w.lower() for w in line.strip().split() if len(w) >= 3]
            if (len(words) == 0):
                continue
            test_neg.append(words)

    return train_pos, train_neg, test_pos, test_neg


def feature_vecs_NLP(train_pos, train_neg, test_pos, test_neg):
    """
    Returns the feature vectors for all text in the train and test datasets.
    """
    # English stopwords from nltk
    stopwords = set(nltk.corpus.stopwords.words('english'))

    # Determine a list of words that will be used as features.
    # This list should have the following properties:
    #   (1) Contains no stop words
    #   (2) Is in at least 1% of the positive texts or 1% of the negative texts
    #   (3) Is in at least twice as many postive texts as negative texts, or vice-versa.

    # YOUR CODE HERE
    def get_word_counts(sentence_list, counts_dict):
        # Define threshold
        # Remove duplicates and stop words
        # Get word counts in positive and negative contexts
        threshold = len(sentence_list) * 0.01
        for word_list in sentence_list:
            word_list = list(
                set([word for word in word_list if word not in stopwords]))
            for word in word_list:
                counts_dict[word] += 1
        return counts_dict

    train_pos_counts = defaultdict(int)
    train_neg_counts = defaultdict(int)

    # The counts_dict now has count, i.e. the number of sentences, for all unique words of the sentence_list.
    # We remove all words from this dictionary which occur less than 1%
    train_pos_counts = get_word_counts(
        train_pos, train_pos_counts)
    train_neg_counts = get_word_counts(
        train_neg, train_neg_counts)

    all_words = []
    for pos_word in train_pos_counts:
        if (train_pos_counts[pos_word] >= len(train_pos) * 0.01) and (train_pos_counts[pos_word] >= 2*train_neg_counts[pos_word]):
            all_words.append(pos_word)

    for neg_word in train_neg_counts:
        if (train_neg_counts[neg_word] >= len(train_neg) * 0.01) and (train_neg_counts[neg_word] >= 2*train_pos_counts[neg_word]):
            all_words.append(neg_word)

    all_words = list(set(all_words))

    # Using the above words as features, construct binary vectors for each text in the training and test set.
    # These should be python lists containing 0 and 1 integers.
    # YOUR CODE HERE
    def get_binary_vectors(sentence_list, all_words):
        bin_sent_vec = []
        for word_list in sentence_list:
            word_list_vec = [0]*len(all_words)
            for word in word_list:
                if word in all_words:
                    word_list_vec[all_words.index(word)] = 1
            bin_sent_vec.append(word_list_vec)
        return bin_sent_vec

    train_pos_vec = get_binary_vectors(train_pos, all_words)
    train_neg_vec = get_binary_vectors(train_neg, all_words)
    test_pos_vec = get_binary_vectors(test_pos, all_words)
    test_neg_vec = get_binary_vectors(test_neg, all_words)

    # Return the four feature vectors
    return train_pos_vec, train_neg_vec, test_pos_vec, test_neg_vec


def feature_vecs_DOC(train_pos, train_neg, test_pos, test_neg):
    """
    Returns the feature vectors for all text in the train and test datasets.
    """
    # Doc2Vec requires TaggedDocument objects as input.
    # Turn the datasets from lists of words to lists of TaggedDocument objects.
    # YOUR CODE HERE
    def labelize_sentences(sentence_list, label_type):
        labelized = []
        for i, words in enumerate(sentence_list):
            label = '%s_%s' % (label_type, i)
            labelized.append(TaggedDocument(words, [label]))
        return labelized

    labeled_train_pos = labelize_sentences(train_pos, "TRAIN_POS")
    labeled_train_neg = labelize_sentences(train_pos, "TRAIN_NEG")
    labeled_test_pos = labelize_sentences(train_pos, "TEST_POS")
    labeled_test_neg = labelize_sentences(train_pos, "TEST_NEG")

    # Initialize model
    model = Doc2Vec(min_count=1, window=10, size=100,
                    sample=1e-4, negative=5, workers=4)
    print("Doc2Vec")
    sentences = labeled_train_pos + labeled_train_neg + \
        labeled_test_pos + labeled_test_neg
    model.build_vocab(sentences)

    # Train the model
    # This may take a bit to run
    for i in range(5):
        print("Training iteration %d" % (i))
        random.shuffle(sentences)
        model.train(sentences, total_examples=model.corpus_count,
                    epochs=model.iter)
    print("end of training")

    # Use the docvecs function to extract the feature vectors for the training and test data
    # YOUR CODE HERE
    # The model.docvecs function allows one to get feature vectors for a specified label

    train_pos_vec = [model.docvecs["TRAIN_POS_" +
                                   str(i)] for i in range(len(labeled_train_pos))]
    train_neg_vec = [model.docvecs["TRAIN_NEG_" +
                                   str(i)] for i in range(len(labeled_train_neg))]
    test_pos_vec = [model.docvecs["TEST_POS_" +
                                  str(i)] for i in range(len(labeled_test_pos))]
    test_neg_vec = [model.docvecs["TEST_NEG_" +
                                  str(i)] for i in range(len(labeled_test_neg))]
    # Return the four feature vectors
    return train_pos_vec, train_neg_vec, test_pos_vec, test_neg_vec


def feature_vecs_DOC_W2V(train_pos, train_neg, test_pos, test_neg):
    """
    Returns the feature vectors for all text in the train and test datasets.
    """
    # Load the pre-trained word2vec model
    word2vec_model = word2vec.Word2Vec.load(path_to_pretrained_w2v)

    # Doc2Vec requires TaggedDocument objects as input.
    # Turn the datasets from lists of words to lists of TaggedDocument objects.
    labeled_train_pos = [TaggedDocument(
        words, ["TRAIN_POS_" + str(i)]) for i, words in enumerate(train_pos)]
    labeled_train_neg = [TaggedDocument(
        words, ["TRAIN_NEG_" + str(i)]) for i, words in enumerate(train_neg)]
    labeled_test_pos = [TaggedDocument(
        words, ["TEST_POS_" + str(i)]) for i, words in enumerate(test_pos)]
    labeled_test_neg = [TaggedDocument(
        words, ["TEST_NEG_" + str(i)]) for i, words in enumerate(test_neg)]

    sentences = labeled_train_pos + labeled_train_neg + \
        labeled_test_pos + labeled_test_neg

    # Use modified doc2vec codes for applying the pre-trained word2vec model
    model = doc2vec_modified.Doc2Vec(dm=0, dm_mean=1, alpha=0.025, min_alpha=0.0001,
                                     min_count=1, size=1000, hs=1, workers=4, train_words=False, train_lbls=True)
    model.reset_weights()

    # Copy wiki word2vec model into doc2vec model
    model.vocab = word2vec_model.vocab
    model.syn0 = word2vec_model.syn0
    model.syn1 = word2vec_model.syn1
    model.index2word = word2vec_model.index2word

    print("# of pre-trained vocab = " + str(len(model.vocab)))

    # Extract sentence labels for the training and test data
    train_pos_labels = ["TRAIN_POS_" + str(i)
                        for i in range(len(labeled_train_pos))]
    train_neg_labels = ["TRAIN_NEG_" + str(i)
                        for i in range(len(labeled_train_neg))]
    test_pos_labels = ["TEST_POS_" + str(i)
                       for i in range(len(labeled_test_pos))]
    test_neg_labels = ["TEST_NEG_" + str(i)
                       for i in range(len(labeled_test_neg))]

    sentence_labels = train_pos_labels + \
        train_neg_labels + test_pos_labels + test_neg_labels

    new_syn0 = empty((len(sentences), model.layer1_size), dtype=REAL)
    new_syn1 = empty((len(sentences), model.layer1_size), dtype=REAL)

    syn_index = 0

    # Initialize and add a vector of syn0 (i.e. input vector) and syn1 (i.e. output vector) for a vector of a label
    for label in sentence_labels:
        # I made this function in the doc2vec code
        v = model.append_label_into_vocab(label)

        random.seed(uint32(model.hashfxn(
            model.index2word[v.index] + str(model.seed))))

        new_syn0[syn_index] = (random.rand(
            model.layer1_size) - 0.5) / model.layer1_size
        new_syn1[syn_index] = zeros((1, model.layer1_size), dtype=REAL)

        syn_index += 1

    model.syn0 = vstack([model.syn0, new_syn0])
    model.syn1 = vstack([model.syn1, new_syn1])

    model.precalc_sampling()

    # Train the model
    # This may take a bit to run
    for i in range(5):
        start_time = time.time()

        print("Training iteration %d" % (i))
        random.shuffle(sentences)
        model.train(sentences)

        print("Done - Training")
        print("--- %s minutes ---" % ((time.time() - start_time) / 60))
        start_time = time.time()

        # Convert "nan" values into "0" in vectors
        indices_nan = isnan(model.syn0)
        model.syn0[indices_nan] = 0.0

        indices_nan = isnan(model.syn1)
        model.syn1[indices_nan] = 0.0

        # Extract the feature vectors for the training and test data
        train_pos_vec = [model.syn0[model.vocab["TRAIN_POS_" +
                                                str(i)].index] for i in range(len(labeled_train_pos))]
        train_neg_vec = [model.syn0[model.vocab["TRAIN_NEG_" +
                                                str(i)].index] for i in range(len(labeled_train_neg))]
        test_pos_vec = [model.syn0[model.vocab["TEST_POS_" +
                                               str(i)].index] for i in range(len(labeled_test_pos))]
        test_neg_vec = [model.syn0[model.vocab["TEST_NEG_" +
                                               str(i)].index] for i in range(len(labeled_test_neg))]

        print("Done - Extracting the feature vectors")
        print("--- %s minutes ---" % ((time.time() - start_time) / 60))

    # Return the four feature vectors
    return train_pos_vec, train_neg_vec, test_pos_vec, test_neg_vec


def build_models_NLP(train_pos_vec, train_neg_vec):
    """
    Returns a BernoulliNB and LosticRegression Model that are fit to the training data.
    """
    Y = ["pos"]*len(train_pos_vec) + ["neg"]*len(train_neg_vec)

    # Use sklearn's BernoulliNB and LogisticRegression functions to fit two models to the training data.
    # For BernoulliNB, use alpha=1.0 and binarize=None
    # For LogisticRegression, pass no parameters
    # YOUR CODE HERE
    X = train_pos_vec + train_neg_vec
    nb_model = sklearn.naive_bayes.BernoulliNB(
        alpha=1.0, binarize=None)
    nb_model.fit(X, Y)

    lr_model = sklearn.linear_model.LogisticRegression()
    lr_model.fit(X, Y)

    return nb_model, lr_model


def build_models_DOC(train_pos_vec, train_neg_vec):
    """
    Returns a GaussianNB and LosticRegression Model that are fit to the training data.
    """
    Y = ["pos"]*len(train_pos_vec) + ["neg"]*len(train_neg_vec)

    # Use sklearn's GaussianNB and LogisticRegression functions to fit two models to the training data.
    # For LogisticRegression, pass no parameters
    # YOUR CODE HERE
    X = train_pos_vec + train_neg_vec
    nb_model = sklearn.naive_bayes.GaussianNB()
    nb_model.fit(X, Y)

    lr_model = sklearn.linear_model.LogisticRegression()
    lr_model.fit(X, Y)

    return nb_model, lr_model


def build_models_DOC_W2V(train_pos_vec, train_neg_vec):
    """
    Returns a GaussianNB and LosticRegression Model that are fit to the training data.
    """
    Y = ["pos"]*len(train_pos_vec) + ["neg"]*len(train_neg_vec)

    # Use sklearn's GaussianNB and LogisticRegression functions to fit two models to the training data.
    # For LogisticRegression, pass no parameters
    X = train_pos_vec + train_neg_vec
    nb_model = sklearn.naive_bayes.GaussianNB()
    nb_model.fit(X, Y)

    lr_model = sklearn.linear_model.LogisticRegression()
    lr_model.fit(X, Y)

    return nb_model, lr_model


def evaluate_model(model, test_pos_vec, test_neg_vec, print_confusion=False):
    """
    Prints the confusion matrix and accuracy of the model.
    """
    # Use the predict function and calculate the true/false positives and true/false negative.
    # YOUR CODE HERE
    X_test = test_pos_vec + test_neg_vec
    Y_test = ["pos"]*len(test_pos_vec) + ["neg"]*len(test_pos_vec)

    Y_pred_test = model.predict(X_test)
    tp = fp = tn = fn = 0
    for ind in range(len(Y_test)):
        if Y_test[ind] == Y_pred_test[ind] == "pos":
            tp += 1
        elif Y_test[ind] == Y_pred_test[ind] == "neg":
            tn += 1
        elif (Y_test == "pos" and Y_pred_test[ind] == "neg"):
            fn += 1
        else:
            fp += 1

    accuracy = float((tp+tn)/(tp+tn+fp+fn))

    if print_confusion:
        print("predicted:\tpos\tneg")
        print("actual:")
        print("pos\t\t%d\t%d" % (tp, fn))
        print("neg\t\t%d\t%d" % (fp, tn))
    print("accuracy: %f" % (accuracy))


if __name__ == "__main__":
    main()
