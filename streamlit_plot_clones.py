
import itertools
import streamlit
import pandas
import plotly_express as px
from plotly.subplots import make_subplots

streamlit.set_page_config(layout="wide")

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
    number_of_plots = len(display_combinations)

    if number_of_plots > 1:

        display_combinations['MultiPlot'] = 'MultiPlot'

        # User input
        sample_combination = display_combinations[streamlit.sidebar.selectbox('Please select which samples to compare', display_combinations.keys())]
    else:
        sample_combination = list(display_combinations.values())[0]

    # User input
    fraction_type = streamlit.sidebar.radio('Select data type', ('VAF', 'pyclone_CCF', 'VAF_CCF'))

    visual_appearance = streamlit.sidebar.expander('Edit visual appearance')

    # User input
    dot_size = visual_appearance.selectbox('Dot size...', range(5, 21), index=7)

    # User input
    display_dot_periphery_line = visual_appearance.checkbox('Toggle dot edge-lines', value=True)

    if display_dot_periphery_line:
        marker = {
            'size': dot_size,
            'line': {
                'width': 2,
                'color': 'DarkSlateGrey'
            }
        }
    else:
        marker = {
            'size': dot_size,
        }

    # Define ranges for axes
    x_y_ranges = ([-0.05, 1.05], [-0.1, 2.1 ])
    range_x = x_y_ranges[0] if fraction_type == 'VAF' else x_y_ranges[1]
    range_y = x_y_ranges[0] if fraction_type == 'VAF' else x_y_ranges[1]

    # Multiplot
    if sample_combination == 'MultiPlot':

        # User input
        grid_columns = visual_appearance.slider('Number of grid columns', min_value=2, max_value=8, value=3, step=1)

        # User input
        inter_space = visual_appearance.slider('Space between plots', min_value=0.05, max_value=0.5, value=0.2, step=0.05)

        grid_rows = int(number_of_plots / grid_columns) + 1 if number_of_plots % grid_columns else int(number_of_plots / grid_columns)

        subplot_size = visual_appearance.slider('Sub-plot size', min_value=100, max_value=800, value=400, step=100)

        subplot_titles = list(display_combinations.keys())[:-1]

        h_space = inter_space / grid_columns
        v_space = inter_space / grid_rows

        figure = make_subplots(cols=grid_columns, rows=grid_rows, subplot_titles=subplot_titles, horizontal_spacing=h_space, vertical_spacing=v_space)

        row = 1
        col = 1
        plot_number = 1
        legend_groups = set()
        for sample_combination in list(display_combinations.values())[:-1]:

            # We currently have no structure to guarantee primary tumors on x axes and metastases on y
            x_y_axes = (fraction_type + '_' + sample_combination[0], fraction_type + '_' + sample_combination[1])

            px_figure = px.scatter(
                data_frame,
                x=x_y_axes[0],
                y=x_y_axes[1],
                range_x=range_x,
                range_y=range_y,
                color="Cluster",
                facet_col="Cluster",
                hover_data={
                    x_y_axes[0]: False,
                    x_y_axes[1]: False,
                    'Cluster': True,
                    "Mutation": True,
                    "Variant_Type": True,
                    'Impact': True,
                    'Gene': True,
                    'Cluster_Assignment_Prob': True
                },
            )

            for trace in px_figure['data']:

                # Avoid having the legend duplicated for each added subplot
                if trace['legendgroup'] in legend_groups:
                    trace['showlegend'] = False
                else:
                    legend_groups.add(trace['legendgroup'])
                figure.add_trace(trace, row=row, col=col)

            plot_number += 1
            row = int(plot_number / grid_columns) + 1 if plot_number % grid_columns else int(plot_number / grid_columns)
            col = plot_number % grid_columns or grid_columns

        figure.update_traces(
            marker=marker,
            # selector=dict(mode='markers'),

        ).update_layout(
            hoverlabel_align='left',  # Necessary for streamlit to make text for all labels align left
            width=subplot_size*grid_columns + (grid_columns - 1) * h_space,
            height=subplot_size*grid_rows + (grid_rows - 1) * v_space,
        ).update_yaxes(
            range=range_y
        ).update_xaxes(
            range=range_x
        )

    # Single Plot
    else:
        plot_widt = visual_appearance.slider('Plot width', min_value=200, max_value=1000, value=800, step=100)

        # We currently have no structure to guarantee primary tumors on x axes and metastases on y. We could implement a manual axis flip
        x_y_axes = (fraction_type + '_' + sample_combination[0], fraction_type + '_' + sample_combination[1])

        figure = px.scatter(data_frame, x=x_y_axes[0], y=x_y_axes[1],
                            range_x=range_x,
                            range_y=range_y,
                            color="Cluster",
                            width=plot_widt, height=plot_widt,
                            # facet_col='Sample',
                            hover_data={
                                x_y_axes[0]: False,
                                x_y_axes[1]: False,
                                'Cluster': True,
                                "Mutation": True,
                                "Variant_Type": True,
                                'Impact': True,
                                'Gene': True,
                                'Cluster_Assignment_Prob': True
                            },
                            )

        figure.update_traces(
            marker=marker,
            selector=dict(mode='markers'),
        ).update_layout(
            hoverlabel_align='left'  # Necessary for streamlit to make text for all labels align left
        )

    streamlit.plotly_chart(figure, theme=None)
