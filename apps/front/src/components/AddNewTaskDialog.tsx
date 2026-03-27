import { Button, Dialog, DialogActions, DialogContent, DialogTitle, TextField } from "@mui/material";
import { FC } from "react";

type AddNewTaskDialogProps = {
    open: boolean;
    onClose: () => void;
    onSave: () => void;
    title: string;
    description: string;
    onTitleChange: (value: string) => void;
    onDescriptionChange: (value: string) => void;
};

const AddNewTaskDialog: FC<AddNewTaskDialogProps> = ({
    open,
    onClose,
    onSave,
    title,
    description,
    onTitleChange,
    onDescriptionChange,
}) => {
    return (
        <Dialog open={open} onClose={onClose}>
            <DialogTitle>Create a New Task</DialogTitle>
            <DialogContent sx={{ minWidth: "400px", display: "flex", flexDirection: "column", gap: 2, pt: 2 }}>
                <TextField
                    label="Title"
                    value={title}
                    onChange={(e) => onTitleChange(e.target.value)}
                    fullWidth
                    placeholder="Enter task title"
                />
                <TextField
                    label="Description"
                    value={description}
                    onChange={(e) => onDescriptionChange(e.target.value)}
                    fullWidth
                    multiline
                    rows={3}
                    placeholder="Enter task description"
                />
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Cancel</Button>
                <Button onClick={onSave} autoFocus variant="contained">
                    Save
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default AddNewTaskDialog;