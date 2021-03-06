# load models

# For some reason importing from keras.models doesn't work well,
# Maybe due to version problems, so importing from tensorflow.keras

from tensorflow.keras.models import load_model, Model
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer

import numpy as np
import os

taylor_swift_model = load_model(os.path.join(os.getcwd(), 'app' , 'models', 'Taylor_Swift.h5'))
kanye_west_model = load_model(os.path.join(os.getcwd(), 'app' , 'models', 'Kanye_West.h5'))
celine_dion_model = load_model(os.path.join(os.getcwd(), 'app' , 'models', 'Celine_Dion.h5'))
eminem_model = load_model(os.path.join(os.getcwd(), 'app' , 'models', 'Eminem.h5'))
adele_model = load_model(os.path.join(os.getcwd(), 'app' , 'models', 'Adele.h5'))
MODELS_LOADED = True


def get_tokenizer(artist_name: str) -> Tokenizer:
    tokenizer_pickle_file = os.path.join(os.getcwd(), 'app', 'data', 'tokenizer_' + artist_name + '.pkl')

    with open(tokenizer_pickle_file, 'rb') as file:
        tokenizer = pickle.load(file)

    return tokenizer


taylor_swift_tok = get_tokenizer('Taylor_Swift')
kanye_west_tok = get_tokenizer('Kanye_West')
adele_tok = get_tokenizer('Adele')
eminem_tok = get_tokenizer('Eminem')
celine_dion_tok = get_tokenizer('Celine_Dion')
TOKS_LOADED = True


SEQ_LEN = 20 # sequence length for LSTMs, i.e., act upon after recalling previous SEG_LEN words
START_TEXT = '| ' * SEQ_LEN


def sample(preds, temperature=0.2) -> 'Temperature sampled observations':
  preds = np.asarray(preds).astype('float64')
  preds = np.log(preds) / temperature
  preds_exp = np.exp(preds)

  # The probabilities should be normalized before sampling using np.random.multinomial
  preds = preds_exp / np.sum(preds_exp)

  # Draw samples from preds, which is a multinomial distribution
  probs = np.random.multinomial(1, preds[0], 1)

  return np.argmax(probs)


def gen_text(seed: str, n_next_words: int, seq_len: int, temperature: float, artist_name: str) -> 'Predicted words':
    out_text = ''
    seed = START_TEXT + seed

    if artist_name == 'Taylor_Swift':
        model = taylor_swift_model
        tokenizer = taylor_swift_tok
    elif artist_name == 'Kanye_West':
        model = kanye_west_model
        tokenizer = kanye_west_tok
    elif artist_name == 'Celine Dion':
        model = celine_dion_model
        tokenizer = celine_dion_tok
    elif artist_name == 'Eminem':
        model = eminem_model
        tokenizer = eminem_tok
    elif artist_name == 'Adele':
        model = adele_model
        tokenizer = adele_tok
    else:
        raise NotImplementedError('Only Taylor Swift is available right now!')

    # We shall retrieve new words till we get n_next_words,
    # or till the model wants to start a new song

    for i in range(n_next_words):
        token_list = tokenizer.texts_to_sequences([seed])
        # print(token_list)

        # we can feed in an arbitrary number of words to the LSTM
        # but let's stick to only the last seq_len number of words
        # that'll help it predict faster
        token_list = token_list[0][-seq_len:]  # note that token_list was a list of lists before this line

        # Reshape it and convert to ndarray so that we an feed it in
        token_list = np.reshape(token_list, (1, seq_len))

        # Predict words!
        probs = model.predict(token_list, verbose=0)
        # print(np.shape(probs))

        y_sampled = sample(probs, temperature)

        out_word = tokenizer.index_word[y_sampled] if y_sampled > 0 else ''
        # print(out_word)

        if out_word == '|':  # the model is trying to start a new song... so finish up
            print('New song!')
            break

        if not out_word.endswith('\n'):
            seed += out_word + ' '  # update the seed
            out_text += out_word + ' '
        else:
            seed += out_word + ' '
            out_text += out_word

    return out_text