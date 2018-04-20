import cswEngine
import numpy as np
import tensorflow as tf


""" 
humans versus nets: 
  although I should keep in mind that one of the main goals of the 
  project is to make network and human experiments comparable
  it is also improtant to keep in mind that there are assymetries
  humans have meaning, nets operate on abstractions
  human meaning arises from cascading abstractions
  this brings up the problem of how to appropriate encode net experiments
    so that you don't encode the answer into the problem
    and so the computational problem solved by the net is informative
    of human brain computations


simple scene vectors: sum filler and state vectors to get 
  a unique vector representation for each (state,RFC) pair.
  want flexibility for scenes get encoded as vectors.

LSTM, RNN, control 

nets have two response units corresponding to right or left 
questions encoded as combination of two options

"""


def gen_NetExp(k):
  path_L,RFC_L = cswEngine.Exp().gen_k_paths(k)
  # keep names of nodes only
  path_L2 = [[node.name for node in path if node.type == 'story_node'] for path in path_L]
  # make path_L which is list of lists, into single long list
  L = []
  for path in path_L2:
    L.extend([n for n in path])
  # form vocabulary 
  S = set(L)
  I = np.eye(len(S),dtype=np.float32)
  vocab = {n:idx for idx,n in enumerate(S)}
  # sequence of onehot vectors
  vec_seq = np.array([I[vocab[st]] for st in L])
  return vec_seq


## DATA GENERATION


BATCH_SIZE = 20


def get_XY_matrices(vec_seq):
  # assmble train and test data matrices
  X,Y = [],[]
  for x,y in zip(vec_seq[:-1],vec_seq[1:]):
    X.append(x)
    Y.append(y)
  X = np.array(X)
  Y = np.array(Y)
  return X,Y

def get_dataset_iterator(vec_seq):
  """ given a sequence of vectors, 
      make train and test data matrices
      return tensorflow dataset for training
  """

  n_states = len(vec_seq[0])

  X,Y = get_XY_matrices(vec_seq)
  # parametrized dataset
  # X = tf.placeholder(tf.float32,shape=[-1,len(vec_seq[0])])
  # Y = tf.placeholder(tf.float32,shape=[-1,len(vec_seq[0])])
  train_ds = tf.data.Dataset.from_tensor_slices((X,Y))
  train_ds = train_ds.repeat()
  train_ds = train_ds.shuffle(100000)
  train_ds = train_ds.apply(
    tf.contrib.data.batch_and_drop_remainder(BATCH_SIZE))
  train_itr = train_ds.make_one_shot_iterator()
  # test dataset
  X_test = tf.one_hot(indices=np.arange(n_states),depth=n_states)
  test_ds = tf.data.Dataset.from_tensor_slices(X_test)
  test_itr = test_ds.make_one_shot_iterator()
  return train_itr,test_itr

def setup_tfds(X_ph,Y_ph,batch_size_ph):
  """ make parametrized (feedable) dataset 
      then make iterator which gets initialized 
        with either train or test data"""

  with tf.variable_scope('dataset'):
    # train
    tfds_train = tf.data.Dataset.from_tensor_slices((X_ph,Y_ph))
    tfds_train = tfds_train.repeat()
    tfds_train = tfds_train.shuffle(500000)
    tfds_train = tfds_train.apply(
      tf.contrib.data.batch_and_drop_remainder(batch_size_ph)) 


    # test
    tfds_test = tf.data.Dataset.from_tensor_slices((X_ph,Y_ph))
    tfds_test = tfds_test.apply(
      tf.contrib.data.batch_and_drop_remainder(batch_size_ph)) 

    # iterator
    itr = tf.data.Iterator.from_structure(
                tfds_test.output_types,
                tfds_test.output_shapes)

    train_itr_initop = itr.make_initializer(tfds_train)
    test_itr_initop = itr.make_initializer(tfds_test)

  # itr = itr
  batch_x,batch_y = itr.get_next()
  return batch_x,batch_y,train_itr_initop,test_itr_initop


## SIMPLE FEED FORWARD NETWORK 


def get_layer(dims,lname):
  with tf.variable_scope('params_%s'%lname):
    W = tf.get_variable(name="weight",
          initializer=tf.contrib.layers.xavier_initializer(),
          shape=[dims[0],dims[1]])
    b = tf.get_variable(name="bias",
          initializer=tf.contrib.layers.xavier_initializer(),
          shape=[dims[1]])
  return W,b

def setup_inference(batch_x,layer_dims):
  """ make an object which encodes network structure
  which holds layer names, layer dimensions and activation functions
  """

  with tf.variable_scope('layer0_linear'):
    W_0,b_0 = get_layer(layer_dims[0],'layer0')
    XW_0 = tf.matmul(batch_x,W_0)
    act_0 = tf.nn.bias_add(XW_0,b_0,name='act')

  with tf.variable_scope('layer1_elu'):
    W_1,b_1 = get_layer(layer_dims[1],'layer1')
    AW_1 = tf.matmul(act_0,W_1)
    preact_1 = tf.nn.bias_add(AW_1,b_1,name='preact')
    act_1 = tf.nn.elu(preact_1, name='act_1')

  with tf.variable_scope('layer2_softmax'):
    W_2,b_2 = get_layer(layer_dims[2],'layer1')
    AW_2 = tf.matmul(act_0,W_2)
    preact_2 = tf.nn.bias_add(AW_2,b_2,name='preact')
    yhat = tf.nn.softmax(preact_2, name='act_2_softmax')

  # with tf.variable_scope('yaht_onehot'):
  #   yhat_idx = tf.argmax(act_2, axis=1, name='argmax_idx') # index
  #   yhat = tf.one_hot(indices=yhat_idx,depth=layer_dims[2][1])
  #   print(yhat)

  return yhat








## ACCURACY MEASURES

def get_01_accuracy(prediction, actual, embedding):
  """ batch accuracy:
      returns proportion of vectors in prediction (y_hat) whose closest vectors
      are equal to the actual vectors (y)
  """
  print("-USING 01 ACCURACY FOR EMBEDDING VECTOR TYPE-")
  actual_indices = get_closest_cosinesimilarity(actual, embedding)
  prediction_indices = get_closest_cosinesimilarity(prediction, embedding) 
  acc = tf.reduce_mean(
    tf.cast(
      tf.equal(actual_indices, prediction_indices), 
      tf.float32)
    )
  return acc

def get_closest_cosinesimilarity(batch_array, embedding):
  """ normalizes batch and embedding, compute cosine 
      and return index of embedding with largest cosine 
      i.e. returns index to vector in vocabulary closest to those in batch_array
  """
  if len(batch_array.shape) < 2: # cswEngine.expand dims if batch size 1
    batch_array = tf.expand_dims(batch_array, axis=0)  
  else: 
    batch_array 
  # normalize
  normed_embedding = tf.cast(
    tf.nn.l2_normalize(embedding, axis=1), 
    tf.float32)
  normed_array = tf.cast(
    tf.nn.l2_normalize(batch_array, axis=1), 
    tf.float32)
  # compute cos
  cosine_similarity = tf.matmul(
    normed_array, 
    tf.transpose(normed_embedding, [1, 0]))
  return tf.argmax(cosine_similarity, axis=1)


















