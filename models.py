from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
import math
import numpy
import csv
from django.utils.translation import ugettext as _


author = 'Jana B. Jarecki'

doc = """
Risk sensitive foraging
"""

class Constants(BaseConstants):
  name_in_url = 'rsf'
  players_per_group = None
  num_repetitions = 2
  num_trials = 5
  num_multitrial = num_trials * num_repetitions
  num_oneshot = 6
  num_rounds = num_multitrial + num_oneshot
  point_label = _('Points')
  trial_label = _('Choice')
  action_label = _('Option')
  initial_state = 0
  num_actions = 2
  lang = 'en'

class Subsession(BaseSubsession):
  def creating_session(self):
  # Executed at the very start, loops through each num_trial  
    if self.round_number == 1:
      environments = self.load_choice_environment('risk_sensitive_foraging/environment.csv')
      for p in self.get_players():
        # Randomize what is shown when and where
        rnd_environments = self.randomize_row_order(environments)
        rnd_environments = environments
        rnd_actions = self.randomize_col_order(rnd_environments, 0, Constants.num_actions)
        #rnd_environments = numpy.array(rnd_environments)


        p.participant.vars['actions'] = rnd_actions       
        p.participant.vars['budgets'] = numpy.array([x[2][0] for x in rnd_environments])
        self.session.vars['num_actions'] = Constants.num_actions
        self.session.vars['num_blocks'] = len(environments)

        # Predefine random outcomes of all options in all trials
        p.participant.vars['outcomes'] = [ [ p.draw_outcomes(gamble, Constants.num_trials + 1) for gamble in a] for a in rnd_actions]
        
        # Initial values
        p.successes = 0
        p.block = 0
        p.trial = 1
        p.state = Constants.initial_state
        p.budget = p.participant.vars['budgets'][p.block]
        p.set_xp(p.participant.vars['actions'][p.block])


    if (self.round_number > 1) & self.is_multitrial():
      for p in self.get_players():
        # At the start of each new trial
        lastp = p.in_round(self.round_number - 1)
        p.trial = lastp.trial + 1
        p.block = lastp.block
        p.budget = lastp.budget
        p.set_xp(p.participant.vars['actions'][p.block])

        if self.is_new_block():
          # At the start of a new block
          p.block = lastp.block + 1
          p.trial = 1
          p.state = Constants.initial_state
          p.budget = p.participant.vars['budgets'][p.block]
          p.set_xp(p.participant.vars['actions'][p.block])

    if (self.round_number - 1) == Constants.num_multitrial:
      critical_trials = self.load_choice_environment('risk_sensitive_foraging/critical_trials.csv')

      for p in self.get_players():
        rnd_critical_trials = self.randomize_row_order(critical_trials)
        rnd_critical_actions = self.randomize_col_order(rnd_critical_trials, 0, Constants.num_actions)
        rnd_critical_trials = numpy.array(rnd_critical_trials)

        p.participant.vars['critical_actions'] = rnd_critical_actions       
        p.participant.vars['critical_budgets'] = numpy.array([x[2][0] for x in rnd_critical_trials])
        p.participant.vars['critical_trials'] = numpy.array([x[2][1] for x in rnd_critical_trials])
        p.participant.vars['critical_states'] = numpy.array([x[2][2] for x in rnd_critical_trials])
        self.session.vars['critical_num_blocks'] = len(critical_trials)

        # Initial values
        p.block = 0
        p.trial = p.participant.vars['critical_trials'][p.block]
        p.state = p.participant.vars['critical_states'][p.block]
        p.budget = p.participant.vars['critical_budgets'][p.block]
        p.set_xp(p.participant.vars['critical_actions'][p.block])


    if (self.round_number - 1) > Constants.num_multitrial:
      for p in self.get_players():  
        lastp = p.in_round(self.round_number - 1)   
        p.block = lastp.block + 1
        p.trial = p.participant.vars['critical_trials'][p.block]
        p.state = p.participant.vars['critical_states'][p.block]
        p.budget = p.participant.vars['critical_budgets'][p.block]
        p.set_xp(p.participant.vars['critical_actions'][p.block])


  def load_choice_environment(self, filepath):
    with open(filepath) as csvfile:
      next(csvfile)
      the_environments = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
      environments = [[row[ :4], row[4:8], row[8: ]] for row in the_environments]
    return environments

  def randomize_row_order(self, x):
    # x is the list with environments
    rnd_x = x.copy()
    random.shuffle(rnd_x) # Random order
    return rnd_x

  def randomize_col_order(self, x, first, last):
    # x is the environment, first, last is the row index of the actions
    x = [y[ first : last ] for y in x]
    for a in x:
      random.shuffle(a)
    return x

  def is_new_block(self):
    return (self.round_number - 1) % Constants.num_trials == 0

  def is_multitrial(self):
    xx = (self.round_number - 1) < Constants.num_multitrial
    print(" ---- is Multitrial is:", xx)
    return xx

  pass



class Group(BaseGroup):
  pass

# Every round the playder object is re-initialized
class Player(BasePlayer):
  block = models.IntegerField(doc = "Current block")
  trial = models.IntegerField(doc = "Current trial (of 5)")  
  state = models.IntegerField(doc = "State before the current decision")
  budget = models.IntegerField(doc = "Earnings requirement in current block")
  choice = models.IntegerField(doc = "Choice in this trial, 0 = left option, 1 = right option")
  outcome = models.IntegerField(doc = "Randomly drawn outcome of the chosen option given the choice in this trial")
  successes = models.IntegerField(doc = "Number of blocks where the earnings requirement (budget) was reached")
  left_x1 = models.IntegerField(doc = "Outcome 1 of the option that was shown on the left (option position was randomized across participants)")
  left_x2 = models.IntegerField(doc = "Outcome 2 of the option that was shown on the left (option position was randomized across participants)")
  left_p1 = models.FloatField(doc = "Probability of outcome 1 of the option that was shown on the left (option position was randomized across participants)")
  left_p2 = models.FloatField(doc = "Probability of outcome 2 of the option that was shown on the left (option position was randomized across participants)")
  right_x1 = models.IntegerField(doc = "Outcome 1 of the option that was shown on the right (option position was randomized across participants)")
  right_x2 = models.IntegerField(doc = "Outcome 2 of the option that was shown on the right (option position was randomized across participants)")
  right_p1 = models.FloatField(doc = "Probability of outcome 1 of the option that was shown on the right (option position was randomized across participants)")
  right_p2 = models.FloatField(doc = "Probability of outcome 2 of the option that was shown on the right (option position was randomized across participants)")

  def set_xp(self, actions):
    a = actions[0]
    self.left_x1 = a[0]
    self.left_x2 = a[1]
    self.left_p1 = a[2]
    self.left_p2 = a[3]
    a = actions[1]
    self.right_x1 = a[0]
    self.right_x2 = a[1]
    self.right_p1 = a[2]
    self.right_p2 = a[3]

  def draw_outcomes(self, action, size):
    x = action[ :2]
    p = action[2: ][1]
    indices = [0, 1, 0, 1, 1, 0, 1, 0, 1, 1]
    #indices = numpy.random.binomial(n=1, p=p, size=size)
    res = [x[i] for i in indices]
    return res

  def get_outcome(self):
    self.outcome = self.participant.vars['outcomes'][self.block][self.choice][self.trial]

  def get_last_state(self):
    lastself = self.in_round(self.round_number - 1)
    return lastself.state + lastself.outcome

  def update_successes(self):
    state = self.state + self.outcome
    if state >= self.budget:
      if self.round_number == 1:
        self.successes += 1
      else:
        if self.state < self.budget: # self.state is the state at the beginning of this trial
          self.successes += 1
  
  def get_last_success(self):
    return self.in_round(self.round_number - 1).successes

pass