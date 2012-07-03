from chaco.api import Plot, ArrayPlotData
from traits.api import HasTraits, Instance, Bool, Enum

class FrequencyPlot(HasTraits):
    plot = Instance(Plot)
    plotdata = Instance(ArrayPlotData, ())
    plot_all = Bool(False)
    yscale = Enum(['linear', 'log'])

    def __init__(self, model):
        super(FrequencyPlot, self).__init__(model=model)

    def _plot_default(self):
        plot = Plot(self.plotdata)
        return plot

    def update_plotdata(self):
        self.plotdata.set_data("response", self.model.dBmag)

    def get_plot_component(self):
        self.plotdata.set_data("index", self.model.F)
        self.plotdata.set_data("response", self.model.dBmag)
        self.plot.plot(("index", "response"), type="line", index_scale="log")
        return self.plot
