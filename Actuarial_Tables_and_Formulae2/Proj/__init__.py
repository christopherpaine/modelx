from modelx.serialize.jsonvalues import *

_formula = None

_bases = []

_allow_none = None

_spaces = []

# ---------------------------------------------------------------------------
# Cells

def discount_rate(i,t):

    df = age(t)
    # Create a new column 'discount_rate' by multiplying t by 0.04
    df['discount_rate'] = ((1+i)**(1-t))

    return df


def annuity_payment(t):

    df = age(t)
    # Create a new column 'discount_rate' by multiplying t by 0.04
    df['annuity_payment'] = 1

    return df


def mort_rate(t):


    values = age(t).merge(AM92,left_on='age_at_t',right_on='Age x',how='left')
    values.rename(columns={'Duration 2': 'mort_rate_t'}, inplace=True)
    return values[["age_at_t","mort_rate_t"]]


def age(t):

    df1 = age_at_entry+t
    df2 = df1.to_frame()
    df2.rename(columns={'age_at_entry': 'age_at_t'}, inplace=True)

    return df2


def a_due(i):
    summ = 0
    for j in range(122):

        summ += epv_cf(i,j).isna(0)


    return summ["epv_cf"]


def age_at_entry():





    return model_points["age_at_entry"]


def prob_if(t):
    #probability IF at end of t
    product = 1
    #print(range(t+1))
    for i in range(t + 1):
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

    # Verify the new dataframe
    #print(df)


    return df


def surv_rate(t):

    df = mort_rate(t)
    #print(df)
    df['mort_rate_t'] = 1 - df['mort_rate_t']
    df.rename(columns={'mort_rate_t': 'surv_rate_t'}, inplace=True)
    return df


def epv_cf(i,t):

    df = age(t)
    df["epv_cf"] = annuity_payment(t)["annuity_payment"]*discount_rate(i,t)["discount_rate"]*prob_if(t)["prob_if_t"]



    return df


# ---------------------------------------------------------------------------
# References

AM92 = ("IOSpec", 2057374163152, 2057374165696)

model_points = ("IOSpec", 2057379691728, 2057374164976)