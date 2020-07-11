def total_sentiments(sent_dict_array):
  total = 0
  for state_dict in sent_dict_array:
    for state in state_dict:
      sent_dict = state_dict[state]
      for sent in sent_dict:
        total += sent_dict[sent]
  return total

def total_indivudual_sentiments(sent_dict_array):
  ind_sent_count_dict = {}
  for state_dict in sent_dict_array:
    for state in state_dict:
      sent_dict = state_dict[state]
      for sent in sent_dict:
        if sent in ind_sent_count_dict:
          ind_sent_count_dict[sent] += sent_dict[sent]
        else:
          ind_sent_count_dict[sent] = sent_dict[sent]
  return ind_sent_count_dict

def get_tone_labels(sent_dict_array):
  tone_labels_array = []
  for state_dict in sent_dict_array:
    for state in state_dict:
      sent_dict = state_dict[state]
      for sent in sent_dict:
        if sent not in tone_labels_array:
          tone_labels_array.append(sent)
  return tone_labels_array

def total_sentiment_count_per_state(sent_dict_array):
  total_sentiment_count_per_state_dict = {}
  for states_dict in sent_dict_array:
    for state in states_dict:
      if state in total_sentiment_count_per_state_dict:
        for sent in total_sentiment_count_per_state_dict[state]:
          total_sentiment_count_per_state_dict[state][sent] += states_dict[state][sent]
      else:
        total_sentiment_count_per_state_dict[state] = states_dict[state]
  return total_sentiment_count_per_state_dict

def total_sentiment_count_per_date(datewise_sentiments):
  total_datewise_sentiments = {}
  for date_sent_dict in datewise_sentiments:
    for date in date_sent_dict:
      if date in total_datewise_sentiments:
        for sentiments_of_date in total_datewise_sentiments[date]:
          total_datewise_sentiments[date][sentiments_of_date] += date_sent_dict[date][sentiments_of_date]
      else:
        total_datewise_sentiments[date] = date_sent_dict[date]
  return total_datewise_sentiments

def max_sentiment(ind_sent_count_dict):
  max_sentiment_key = list(ind_sent_count_dict.keys())[0]
  for key in ind_sent_count_dict:
    if ind_sent_count_dict[key] > ind_sent_count_dict[max_sentiment_key]:
      max_sentiment_key = key
  return {
    'sentiment': max_sentiment_key,
    'value': ind_sent_count_dict[max_sentiment_key]
  }

def add_OR_in_strings(keyword_model_list):
  output_string = ""
  for keyword_model in keyword_model_list:
    keyword = keyword_model.keyword
    output_string = output_string + keyword + " OR "
  return output_string[:-4]