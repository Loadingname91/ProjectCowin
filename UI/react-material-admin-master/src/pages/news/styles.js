import { makeStyles } from "@material-ui/styles";

export default makeStyles((theme) => ({
  card: {
    minHeight: "100%",
    display: "flex",
    flexDirection: "column",
  },
  cardContent: {
    display: "flex",
    flexGrow: 1,
    flexDirection: "column",
    justifyContent: "space-between",
  },
}));
