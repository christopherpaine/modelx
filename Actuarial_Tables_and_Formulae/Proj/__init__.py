from modelx.serialize.jsonvalues import *

_formula = None

_bases = []

_allow_none = None

_spaces = []

# ---------------------------------------------------------------------------
# Cells

def discount_rate(i,t):
    '''
    a 2 parameter function that takes our age of each model point at time t  i.e. age(t)
    and creates a discount factor such that
    at t=0 we have a factor of 1 year

    the end result is a column for the 'age_at_t' for each model point
    and a column for the discount point
    (is there a concern here with duplicating age_at_t)

    '''
    df = age(t).copy()
    # Create a new column 'discount_rate' by multiplying t by 0.04
    df['discount_rate'] = ((1+i)**-(t))

    return df


def annuity_payment(t):
    '''
    takes age_at_t and creates a column for this
    the second column is the annuity payment for that life
    and is set to 1

    it is this feature that means we have a lifetime annuity since they continue regardless of age.
    '''
    df = age(t).copy()
    # Create a new column 'discount_rate' by multiplying t by 0.04
    df['annuity_payment'] = 1

    return df


def mort_rate(t):
    '''
    takes out AM92 dataframe of mortality rates
    and joins with our age_at_t table

    consequently we return age and mortality rate for that life at t

    we choose duration 2 i.e. multiple rates

    ideally we would have multiple tables and parameterise the AM92 aspect
    with this in mind, an appropriate place to specify the AM92
    would be within the model point file
    '''
    values = age(t).merge(AM92,left_on='age_at_t',right_on='Age x',how='left')
    values.rename(columns={'Duration 2': 'mort_rate_t'}, inplace=True)
    return values[["age_at_t","mort_rate_t"]]


def age(t):
    '''
    takes out age_at_entry and increments each 
    as our time parameter advance
    '''
    df1 = age_at_entry+t
    df2 = df1.to_frame()
    df2.rename(columns={'age_at_entry': 'age_at_t'}, inplace=True)

    return df2


def a_due(i):
    '''
    '''
    df = a_arrears(i).copy()
    df["epv_cf"] = df["epv_cf"]

    return df


def age_at_entry():
    '''
    takes our model point data frame (which currently is a list of ages 17 to 120)
    and reads it into this cell
    '''


    return model_points["age_at_entry"]


def prob_if(t):
    '''
    returns age_at_t
    and a survival function

    '''
    if t==0:
        product =1
    else:    
        #probability IF at end of t
        product = 1
        #print(range(t+1))
        for i in range(t):
            #print (i)
            #print (surv_rate(i))
            product *= surv_rate(i)

    #we now have our probabilities in product["surv_rate_t"]

    import pandas as pd

    # Assuming you already have the two dataframes 'surv_rate' and 'product'

    # Create a new dataframe 'df' by concatenating the columns of interest
    df = pd.concat([surv_rate(t)['age_at_t'], product['surv_rate_t']], axis=1)

    # Rename the columns in the new dataframe
    df.columns = ['age_at_t', 'prob_if_t']

    return df


def surv_rate(t):
    '''
    returns age_at_t and surv_rate_t
    whereby surv_rate_t is simply 1 minus mortality rate
    '''
    df = mort_rate(t)
    #print(df)
    df['mort_rate_t'] = 1 - df['mort_rate_t']
    df.rename(columns={'mort_rate_t': 'surv_rate_t'}, inplace=True)
    return df


def epv_cf(i,t):
    '''
    multiplication of annuity payment ,  discountr rate , probability if for each t
    note this function is specific to our annuity product
    so we may want to parameterise the product in future
    when the model expands
    '''
    df = age(t).copy()
    df["epv_cf"] = annuity_payment(t)["annuity_payment"]*discount_rate(i,t)["discount_rate"]*prob_if(t)["prob_if_t"]



    return df


def a_arrears(i):
    '''
    i don't like having to import within a function, what is the proper way to do this
    we have a hardcoded end point for the loop which should really be determined
    from the entries in epv_cf instead
    we loop over time and add together column of epv_cf to give use expected npv 
    for each model point
    we then concatenate back in our age_at_t column at time 0
    in practice it may be better to have a function that has time as a parameter
    so that we calculated the annuity function at any time
    '''
    import pandas as pd
    summ = 0
    for j in range(122):
         summ += (epv_cf(i,j).fillna(0))
    #summ = summ.to_frame()
    df = pd.concat([epv_cf(i,0)['age_at_t'], summ['epv_cf']], axis=1)
    return df


# ---------------------------------------------------------------------------
# References

AM92 = ("IOSpec", 1557857367280, 1557850446944)

model_points = ("IOSpec", 1557857366944, 1557850028928)