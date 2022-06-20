import React, { useState, useEffect } from "react";
import {
  Grid,
  LinearProgress,
  Select,
  OutlinedInput,
  MenuItem,
  Button,
} from "@material-ui/core";
import { useTheme } from "@material-ui/styles";
import {
  ResponsiveContainer,
  ComposedChart,
  AreaChart,
  LineChart,
  Line,
  Area,
  PieChart,
  Pie,
  Cell,
  YAxis,
  XAxis,
} from "recharts";

// styles
import useStyles from "./styles";

// components
import mock from "./mock";
import Widget from "../../components/Widget";
import PageTitle from "../../components/PageTitle";
import { Typography } from "../../components/Wrappers";
import Dot from "../../components/Sidebar/components/Dot";
import Table from "./components/Table/Table";
import BigStat from "./components/BigStat/BigStat";

const PieChartData = [
  { name: "Group A", value: 400, color: "primary" },
  { name: "Group B", value: 300, color: "secondary" },
  { name: "Group C", value: 300, color: "warning" },
  { name: "Group D", value: 200, color: "success" },
];

export default function Dashboard(props) {
  var classes = useStyles();
  var theme = useTheme();

  // local
  var [mainChartState, setMainChartState] = useState("monthly");

  let [isLoading, setIsLoading] = useState(true);
  let [historiccovidStatsLoading, setHistoricCovidStatsLoading] = useState(
    true,
  );
  let [predictions, setPredictions] = useState([]);
  let [predictionsLoading, setPredictionsLoading] = useState(true);
  let [error, setError] = useState(null);

  let [covidStats, setCovidStats] = useState([]);

  let [historiccovidStats, setHistoricCovidStats] = useState([]);

  function getUSHistoricDaily() {
    return fetch("https://api.covidtracking.com/v1/us/daily.json", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((res) => {
        if (res.status !== 200) {
          throw new Error("Something went wrong on api server!");
        }
        return res.json();
      })
      .then((data) => {
        setHistoricCovidStats(data);
        setHistoricCovidStatsLoading(false);
      })
      .catch((error) => {
        setError(error);
        setHistoricCovidStatsLoading(true);
      });
  }

  function getUSCurrentDaily() {
    return fetch("https://api.covidtracking.com/v1/us/current.json", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((res) => res.json())
      .then((data) => {
        setCovidStats(data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.log("API exception", err);
        setError(err);
        setIsLoading(true);
      });
  }

  function getPredctions() {
    return fetch("http://localhost:8000/api/ml_prediction/", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("access")}`,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        setPredictions(data);
        setPredictionsLoading(false);
      })
      .catch((err) => {
        console.log("API exception", err);
        setError(err);
        setPredictionsLoading(true);
      });
  }

  useEffect(() => {
    getUSCurrentDaily();
    getUSHistoricDaily();
    getPredctions();
  }, []);

  function getBase64Image(img) {
    // Create an empty canvas element
    var canvas = document.createElement("canvas");
    canvas.width = img.width;
    canvas.height = img.height;

    // Copy the image contents to the canvas
    var ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);

    // Get the data-URL formatted image
    // Firefox supports PNG and JPEG. You could check img.src to guess the
    // original format, but be aware the using "image/jpg" will re-encode the image.
    var dataURL = canvas.toDataURL("image/png");

    return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
  }

  let finalLoad = isLoading || historiccovidStatsLoading || predictionsLoading;

  const mainChartData = !finalLoad ? getMainChartData(historiccovidStats) : [];

  // console.log(mainChartData);
  return (
    <>
      <PageTitle title="Dashboard" />
      {finalLoad ? (
        <LinearProgress />
      ) : (
        <Grid container spacing={4}>
          <Grid item lg={6} md={5} sm={6} xs={12}>
            <Widget
              title="US Covid Positive Cases Today"
              upperTitle
              bodyClass={classes.fullHeightBody}
              className={classes.card}
            >
              <div className={classes.visitsNumberContainer}>
                <Grid container item alignItems={"center"}>
                  <Grid item xs={6}>
                    <Typography size="xl" weight="medium" noWrap>
                      {covidStats[0].positive}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <LineChart
                      width={100}
                      height={30}
                      data={historiccovidStats.slice(0, 6).map((item) => {
                        return {
                          name: item.date,
                          value: item.positive,
                        };
                      })}
                    >
                      <Line
                        type="natural"
                        dataKey="value"
                        stroke={theme.palette.success.main}
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </Grid>
                </Grid>
              </div>
              <Grid
                container
                direction="row"
                justify="space-between"
                alignItems="center"
              >
                <Grid item xs={12}>
                  <Typography
                    color="text"
                    colorBrightness="secondary"
                    noWrap
                    style={{
                      center: "center",
                      justifyContent: "center",
                      alignItems: "center",
                      display: "flex",
                    }}
                  >
                    Positive Increase
                  </Typography>
                  <Typography
                    size="md"
                    style={{
                      center: "center",
                      justifyContent: "center",
                      alignItems: "center",
                      display: "flex",
                    }}
                  >
                    {covidStats[0].positiveIncrease}
                  </Typography>
                </Grid>
              </Grid>
            </Widget>
          </Grid>
          <Grid item lg={6} md={5} sm={6} xs={12}>
            <Widget
              title="US Covid Negative Cases Today"
              upperTitle
              bodyClass={classes.fullHeightBody}
              className={classes.card}
            >
              <div className={classes.visitsNumberContainer}>
                <Grid container item alignItems={"center"}>
                  <Grid item xs={6}>
                    <Typography size="xl" weight="medium" noWrap>
                      {covidStats[0].negative}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <LineChart
                      width={100}
                      height={30}
                      data={historiccovidStats.slice(0, 6).map((item) => {
                        return {
                          name: item.date,
                          value: item.negative,
                        };
                      })}
                    >
                      <Line
                        type="natural"
                        dataKey="value"
                        stroke={theme.palette.success.main}
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </Grid>
                </Grid>
              </div>
              <Grid
                container
                direction="row"
                justify="space-between"
                alignItems="center"
              >
                <Grid item xs={12}>
                  <Typography
                    color="text"
                    colorBrightness="secondary"
                    noWrap
                    style={{
                      center: "center",
                      justifyContent: "center",
                      alignItems: "center",
                      display: "flex",
                    }}
                  >
                    Negative Increase
                  </Typography>
                  <Typography
                    size="md"
                    style={{
                      center: "center",
                      justifyContent: "center",
                      alignItems: "center",
                      display: "flex",
                    }}
                  >
                    {covidStats[0].negativeIncrease}
                  </Typography>
                </Grid>
              </Grid>
            </Widget>
          </Grid>
          <Grid item xs={12}>
            <Widget
              bodyClass={classes.mainChartBody}
              header={
                <div className={classes.mainChartHeader}>
                  <Typography
                    variant="h5"
                    color="text"
                    colorBrightness="secondary"
                  >
                    Daily Line Chart
                  </Typography>
                  <div className={classes.mainChartHeaderLabels}>
                    <div className={classes.mainChartHeaderLabel}>
                      <Dot color="warning" />
                      <Typography className={classes.mainChartLegentElement}>
                        Postive
                      </Typography>
                    </div>
                    <div className={classes.mainChartHeaderLabel}>
                      <Dot color="primary" />
                      <Typography className={classes.mainChartLegentElement}>
                        Negative
                      </Typography>
                    </div>
                  </div>
                </div>
              }
            >
              <ResponsiveContainer width="100%" minWidth={500} height={350}>
                <ComposedChart
                  margin={{ top: 0, right: -15, left: -15, bottom: 0 }}
                  data={mainChartData}
                >
                  <YAxis
                    tick={{
                      fill: theme.palette.text.hint + "80",
                      fontSize: 10,
                    }}
                    ticksFormatter={(value) =>
                      value > 100000
                        ? (value / 1000000).toFixed(1) + "l"
                        : value
                    }
                    stroke={theme.palette.text.hint + "80"}
                    tickLine={false}
                  />
                  <XAxis
                    tickFormatter={(i) => i + 10000000}
                    tick={{
                      fill: theme.palette.text.hint + "80",
                      fontSize: 14,
                    }}
                    stroke={theme.palette.text.hint + "80"}
                    tickLine={false}
                  />

                  <Line
                    type="natural"
                    dataKey="negative"
                    stroke={theme.palette.primary.main}
                    strokeWidth={2}
                    dot={false}
                    activeDot={false}
                  />
                  <Line
                    type="linear"
                    dataKey="positive"
                    stroke={theme.palette.warning.main}
                    strokeWidth={2}
                    dot={{
                      stroke: theme.palette.warning.dark,
                      strokeWidth: 2,
                      fill: theme.palette.warning.main,
                    }}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </Widget>
          </Grid>
          <Grid item xs={12}>
            <Widget
              title="Bayesian Prediction by next 10 days"
              upperTitle
              bodyClass={classes.fullHeightBody}
              className={classes.card}
            >
              <div className={classes.visitsNumberContainer}>
                <Grid container item alignItems={"center"}>
                  <Grid item xs={12}>
                    <Typography size="xl" weight="medium" noWrap>
                      {predictions.predictions.bayesian_prediction[
                        "Bayesian Predicted # of Confirmed Cases Worldwide"
                      ].at(-1)}
                    </Typography>
                  </Grid>
                </Grid>
              </div>
            </Widget>
          </Grid>
        </Grid>
      )}
    </>
  );
}

// #######################################################################
function getMainChartData(historiccovidStats) {
  var resultArray = [];
  let lengthValue = historiccovidStats.length - 1;
  for (let i = lengthValue; i > 0; i--) {
    resultArray.push({
      negative: historiccovidStats[i].negative,
      positive: historiccovidStats[i].positive,
    });
  }

  return resultArray;
}
