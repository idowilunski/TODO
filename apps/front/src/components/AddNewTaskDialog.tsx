import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from "@mui/material";
import { FC } from "react";
type AddNewTaskDialogProps = {
    open: boolean;
    onClose: () => void;
    onSave: () => void;
};
const AddNewTaskDialog: FC<AddNewTaskDialogProps> = ({
    open, onClose, onSave
}) => {
    return  <Dialog
        open={open}
        onClose={onClose}
      >
        <DialogTitle>
            {"Create a New Task"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText >
            will do soon    
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={onSave} autoFocus>
            Save
          </Button>
        </DialogActions>
      </Dialog>
}

export default AddNewTaskDialog;