import cv2
import yolov5
from sahi.prediction import ObjectPrediction, PredictionResult
from sahi.utils.cv import visualize_object_predictions

from torchyolo.modelhub.basemodel import YoloDetectionModel


class Yolov5DetectionModel(YoloDetectionModel):
    def load_model(self):
        model = yolov5.load(self.model_path, device=self.device)
        model.conf = self.confidence_threshold
        model.iou = self.iou_threshold
        self.model = model

    def predict(self, image):
        prediction = self.model(image, size=self.image_size)
        object_prediction_list = []
        for _, image_predictions_in_xyxy_format in enumerate(prediction.xyxy):
            for pred in image_predictions_in_xyxy_format.cpu().detach().numpy():
                x1, y1, x2, y2 = (
                    int(pred[0]),
                    int(pred[1]),
                    int(pred[2]),
                    int(pred[3]),
                )
                bbox = [x1, y1, x2, y2]
                score = pred[4]
                category_name = self.model.names[int(pred[5])]
                category_id = pred[5]

                object_prediction = ObjectPrediction(
                    bbox=bbox,
                    category_id=int(category_id),
                    score=score,
                    category_name=category_name,
                )
                object_prediction_list.append(object_prediction)

        prediction_result = PredictionResult(
            object_prediction_list=object_prediction_list,
            image=image,
        )
        if self.save:
            prediction_result.export_visuals(export_dir=self.save_path, file_name=self.output_file_name)

        if self.show:
            image = cv2.imread(image)
            output_image = visualize_object_predictions(image=image, object_prediction_list=object_prediction_list)
            cv2.imshow("Prediction", output_image["image"])
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return prediction_result
