import streamlit as st
import pandas as pd
import numpy as np
import requests
API_ENDPOINT = 'https://c4s1pb1xef.execute-api.us-west-2.amazonaws.com/api/'

# todo: integrate stripe invoice page
# todo: select premades that autofill the checkboxes

# todo: use user info to query api for recommended macros. Show stacked bar plot that shows current selection against
# todo: add settings page to edit your address, health details, etc
# todo: consider saving user purchase history
# todo: integrate recommendations via ordering the options
# todo: see which customer's you're most similar to on 2d graph
# todo: add chart for micronutrient videos
# todo: create a page for videos about the ingredients
# todo: figure out UI for adding more quantity

# todo: tie ordering to shippo api. autoprint on my printer.
# todo in notebook: get nutrients info for all my supplies. make db.
# todo: write line to google balance sheet on order
# todo: create nutrients profile on order. insert into document. send email.
# todo: think about data schema a little more (but not too much more)
# todo: use session state to save user progress incase of webpage crash
# todo: show price per service instead of servings

st.title('🌅 Beoatiful Meals')
categories = ["🥣 base", "🍓 fruit", "🥜 nuts", "🌻 seeds",
              "💥 powder", "💪 protein", "🍫 treats", "🍯 sweetener"]
df = pd.read_csv('nutritional_benefits.csv')
micronutrients = pd.read_csv('micronutrients.csv').set_index('item')

groups = df.groupby('category').item.apply(list).to_dict()
df_ = df.set_index('item')
checkboxes = {}

with st.expander("How this works", True):
    st.markdown('''Easy to order! Start by choosing your base. Then add however many toppings you want.
Once you order, I'll mix it all and send it out — ready to eat!

🚚 FREE Shipping on orders over \$41 (else $10 shipping)

Your total order will make ~30 servings of breakfast!

100% OF PROFITS GO BACK TO HELPING THE HOMELESS IN AUSTIN!

In the spirit of complete transparency, you can view our balance sheet and receipts [here](https://bit.ly/3LT3Bw4).

Start every day off with a nutritionally packed breakfast while at the same time knowing that you're helping end hunger in Austin.

Beoatiful breakfast is almost too easy to make. Just throw some mix in the bowl, add hot water and whala!''')    


col1, col2 = st.columns((1, 1))



def make_int_if_whole(number):
    return int(number) if int(number) == number else number


with col1:
    base = categories[0]
    st.text(f"{base.capitalize()} (choose 1)")

    oats = groups[base][0]
    size = make_int_if_whole(df_.loc['oats']["size"])
    benefits = df_.loc[oats].drop(['category', 'cost', 'size'])
    benefits = ', '.join(benefits[benefits == 1].index)
    checkboxes[oats] = st.checkbox(
        f'{oats} ({size} cups, ${df_.loc["oats", "cost"]})', value=False, help=benefits)


    granola = groups[base][1]
    size = make_int_if_whole(df_.loc[granola, "size"])
    benefits = df_.loc[granola].drop(['category', 'cost', 'size'])
    benefits = ', '.join(benefits[benefits == 1].index)
    checkboxes[granola] = st.checkbox(
        f'{granola} ({size} cups, ${df_.loc[granola, "cost"]})', value=False, help=benefits)

    for category in categories[1:]:
        # todo: add a (1/6) logic to each section
        # todo: pull out the bases from the option logic and make radio button
        selected_num = 0
        with st.expander(f"{category.capitalize()} ({len(df[df.category == category])})"):
            first = df_.loc[groups[category][0]]
            size = make_int_if_whole(first["size"])
            st.text(f'{size} cup, ${first["cost"]} each')
            for option in groups[category]:
                benefits = df_.loc[option].drop(['category', 'cost', 'size'])
                benefits = ', '.join(benefits[benefits == 1].index)
                if option in micronutrients.index:
                    mymicro = micronutrients.loc[option]
                    mymicro = ', '.join(mymicro[mymicro == 1].index)
                else:
                    mymicro = ''
                checkboxes[option] = st.checkbox(
                    option, value=False, help=benefits)

checkboxes = pd.Series(checkboxes, name='selected')
joined = df.set_index('item').join(checkboxes)

with st.sidebar:
    # todo: remove legend from chart
    # todo: title chart ( st.altair_chart)
    # todo: make chart y axis ints
    # idea: sort bars greatest to least?
    benefits = joined[joined.selected == True].drop(
        ['selected', 'category', 'cost', 'size'], axis=1)
    if benefits.sum().sum() == 0:
        st.text('Add some ingredients to see\nyour benefits profile!')
    st.bar_chart(benefits.sum(0))
    total_cost = joined[joined.selected == True].cost.sum()
    total_servings = int(
        np.ceil(joined[joined.selected == True]['size'].sum() / (1/2)))
    # st.write('<style>.header{padding: 10px 16px; background: #555; color: #f1f1f1; position:fixed;top:0 ;left:0;} .sticky { position: fixed; top: 0; width: 100%;} </style><div class="header" id="myHeader">My Total: $'+str(total_cost)+f'</br>Servings: {total_servings}'+f'</br>Until Free Shipping: ${41-total_cost}</div>', unsafe_allow_html=True)

# with st.sidebar:
    st.text(f'My Total: ${total_cost}')
    if total_servings:
        st.text(
            f'Cost Per Serving: ${round(total_cost/total_servings, 2) if total_servings else "":.2f}')
    st.text(f'Until Free Shipping: ${41-total_cost}')

center_col = st.columns(3)[1]

with center_col:
    clicked = st.button('Check Out!')
    if clicked:
        group_counts = joined.groupby('category').selected.sum().drop('🥣 base').astype(int)
        group_counts.index = group_counts.index.to_series().apply(lambda name: name[2:])
        group_counts = group_counts[group_counts > 0]
        if checkboxes[oats]:
            group_counts['oats'] = 1
        elif checkboxes[granola]:
            group_counts['granola'] = 1
        print(group_counts.to_dict())
        response = requests.post(
            f'{API_ENDPOINT}/get_payment_link', json=group_counts.to_dict())
        print(response.text)
        from utils import go_to_link
        # go_to_link(response.text)
        st.markdown("[Click here to complete checkout](%s)" % response.text)
