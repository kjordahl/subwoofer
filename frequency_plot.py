from chaco.api import Plot, ArrayPlotData, PlotAxis
from traits.api import HasTraits, Instance, Bool, Enum

class FrequencyPlot(HasTraits):
    plot = Instance(Plot)
    plotdata = Instance(ArrayPlotData, ())

    def __init__(self, model):
        super(FrequencyPlot, self).__init__(model=model)
        model.set_plot(self)

    def _plot_default(self):
        plot = Plot(self.plotdata)
        return plot

    def update_plotdata(self):
        self.plotdata.set_data("response", self.model.enclosures[0].dBmag)

    def get_plot_component(self):
        self.plotdata.set_data("index", self.model.F)
        self.plotdata.set_data("response", self.model.enclosures[0].dBmag)
        self.plot.plot(("index", "response"), type="line", index_scale="log")
        left = PlotAxis(orientation='left',
                        title='response (dB)',
                        mapper=self.plot.value_mapper,
                        component=self.plot)
        bottom = PlotAxis(orientation='bottom',
                        title='Frequency (Hz)',
                        mapper=self.plot.index_mapper,
                        component=self.plot)
        self.plot.underlays.append(left)
        self.plot.underlays.append(bottom)
        return self.plot
