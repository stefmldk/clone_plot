
import itertools
import streamlit
import pandas
import plotly_express as px

# User input
uploaded_file = streamlit.sidebar.file_uploader("Choose a file to start")

if uploaded_file is not None:
    data_frame = pandas.read_csv(uploaded_file, sep='\t')
    column_names = data_frame.columns
    vaf_columns = [name for name in column_names if (name.startswith('VAF') and not name.startswith('VAF_CCF')) ]
    pyclone_ccf_columns = [name for name in column_names if name.startswith('pyclone')]
    vaf_ccf_columns = [name for name in column_names if name.startswith('CCF')]
    sample_names = [name.split('_')[1] for name in vaf_columns]

    # Combine sample names
    pairwise_sample_combinations = itertools.combinations(sample_names, 2)

    display_combinations = {'{}_vs_{}'.format(combination[0], combination[1]): combination for combination in pairwise_sample_combinations}

    # User input
    sample_combination = display_combinations[streamlit.sidebar.selectbox('Please select which samples to compare', display_combinations.keys())]

    # User input
    fraction_type = streamlit.sidebar.radio('Select data type', ('VAF', 'pyclone_CCF', 'VAF_CCF'))

    combination = (fraction_type + '_' + sample_combination[0], fraction_type + '_' + sample_combination[1])

    figure = px.scatter(data_frame, x=combination[0], y=combination[1],
                        range_x=[-0.1, 2.1],
                        range_y=[-0.1, 2.1],
                        color="Cluster",
                        width=800, height=800,
                        hover_data={
                            combination[0]: False,
                            combination[1]: False,
                            'Cluster': True,
                            "Mutation": True,
                            "Variant_Type": True,
                            'Impact': True,
                            'Gene': True,
                            'Cluster_Assignment_Prob': True
                        },
                        )

    figure.update_traces(
        marker={
            'size': 12,
            'line': {
                'width': 2,
                'color': 'DarkSlateGrey'
            }
        },
        selector=dict(mode='markers'),
    ).update(
        layout_coloraxis_showscale=False  # Don't show color scale for clone colors
    ).update_layout(
        hoverlabel_align='left'  # Necessary for streamlit to make text for all labels align left
    )
    # figure.write_html('{}.html'.format(title))

    streamlit.plotly_chart(figure, theme=None)