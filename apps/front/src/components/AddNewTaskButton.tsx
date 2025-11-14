import { FC } from "react";
import { Button } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
type AddNewTaskButtonProps = {
    onClick: () => void;
};
const AddNewTaskButton: FC<AddNewTaskButtonProps> = ({
    onClick,
}) => {
    return (
        <Button
            variant="contained"
            startIcon={<AddIcon />}
            sx={{
                borderRadius: 2,
                textTransform: "none",
                px: 3,
                py: 1.5,
            }}
            onClick={onClick}
        >
            Add New Task
        </Button>
    );
};

export default AddNewTaskButton;