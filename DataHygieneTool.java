import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.io.File;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class DataHygieneTool extends JFrame implements ActionListener {

    // GUI components
    JComboBox<String> directoryBox;
    JButton browseBtn, runScanBtn, applyBtn, exportBtn, viewLogBtn;

    // Rule checkboxes
    JCheckBox namingRule, metadataRule, organizeRule, removeRule, archiveRule, customRule;

    // Progress bar
    JProgressBar progressBar;

    // Labels for scan information
    JLabel scannedLabel, updatedLabel, etaLabel;

    // Area to show preview of changes
    JTextArea previewArea;

    // File chooser for selecting directories
    JFileChooser chooser;

    // Counters
    int scanned = 0;
    int updated = 0;

    // Simple HTTP client
    private HttpClient httpClient;
    private static final String API_URL = "http://localhost:5000";

    // Constructor creates the GUI
    public DataHygieneTool() {

        setTitle("Data Hygiene Tool");
        setSize(1000,700);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        // Initialize HTTP client
        httpClient = HttpClient.newHttpClient();

        // Top panel (directory selection)
        JPanel topPanel = new JPanel();

        directoryBox = new JComboBox<>();
        directoryBox.setPreferredSize(new Dimension(400,25));

        browseBtn = new JButton("Browse");
        runScanBtn = new JButton("Run Scan");

        browseBtn.addActionListener(this);
        runScanBtn.addActionListener(this);

        topPanel.add(new JLabel("Select Directory to Scan:"));
        topPanel.add(directoryBox);
        topPanel.add(browseBtn);
        topPanel.add(runScanBtn);

        add(topPanel,BorderLayout.NORTH);

        // Center panel
        JPanel centerPanel = new JPanel();
        centerPanel.setLayout(new GridLayout(1,2));

        // Rules panel
        JPanel rulesPanel = new JPanel();
        rulesPanel.setBorder(BorderFactory.createTitledBorder("Data Hygiene Rules"));
        rulesPanel.setLayout(new GridLayout(6,1));

        namingRule = new JCheckBox("Apply File Naming Conventions");
        metadataRule = new JCheckBox("Update File Metadata");
        organizeRule = new JCheckBox("Organize Files by Category");
        removeRule = new JCheckBox("Remove Irrelevant Files");
        archiveRule = new JCheckBox("Archive Outdated Files");
        customRule = new JCheckBox("Custom Rules");

        rulesPanel.add(namingRule);
        rulesPanel.add(metadataRule);
        rulesPanel.add(organizeRule);
        rulesPanel.add(removeRule);
        rulesPanel.add(archiveRule);
        rulesPanel.add(customRule);

        centerPanel.add(rulesPanel);

        // Progress panel
        JPanel progressPanel = new JPanel();
        progressPanel.setBorder(BorderFactory.createTitledBorder("Scan Progress"));
        progressPanel.setLayout(new GridLayout(5,1));

        progressBar = new JProgressBar();

        scannedLabel = new JLabel("Files Scanned: 0");
        updatedLabel = new JLabel("Files Updated: 0");
        etaLabel = new JLabel("ETA: 00:00");

        progressPanel.add(progressBar);
        progressPanel.add(scannedLabel);
        progressPanel.add(updatedLabel);
        progressPanel.add(etaLabel);

        centerPanel.add(progressPanel);

        add(centerPanel,BorderLayout.CENTER);

        // Bottom panel
        JPanel bottomPanel = new JPanel(new BorderLayout());

        // Summary panel
        JPanel summaryPanel = new JPanel();
        summaryPanel.setBorder(BorderFactory.createTitledBorder("Scan Summary"));
        summaryPanel.setLayout(new GridLayout(6,1));

        summaryPanel.add(new JLabel("Renamed Files: 0"));
        summaryPanel.add(new JLabel("Metadata Updated: 0"));
        summaryPanel.add(new JLabel("Files Organized: 0"));
        summaryPanel.add(new JLabel("Irrelevant Files Removed: 0"));
        summaryPanel.add(new JLabel("Files Archived: 0"));

        applyBtn = new JButton("Apply Corrections");
        applyBtn.addActionListener(this);

        summaryPanel.add(applyBtn);

        bottomPanel.add(summaryPanel,BorderLayout.WEST);

        // Preview panel
        JPanel previewPanel = new JPanel(new BorderLayout());
        previewPanel.setBorder(BorderFactory.createTitledBorder("Preview Changes"));

        previewArea = new JTextArea();
        JScrollPane scroll = new JScrollPane(previewArea);

        previewPanel.add(scroll,BorderLayout.CENTER);

        // Buttons under preview
        JPanel previewButtons = new JPanel();

        viewLogBtn = new JButton("View Log File");
        exportBtn = new JButton("Export Results");

        previewButtons.add(viewLogBtn);
        previewButtons.add(exportBtn);

        previewPanel.add(previewButtons,BorderLayout.SOUTH);

        bottomPanel.add(previewPanel,BorderLayout.CENTER);

        add(bottomPanel,BorderLayout.SOUTH);

        // File chooser setup
        chooser = new JFileChooser();
        chooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);

        setVisible(true);
    }

    // Simple method to call Python backend
    private void callPythonBackend(String endpoint, String jsonData) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(API_URL + endpoint))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(jsonData))
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            SwingUtilities.invokeLater(() -> {
                if (response.statusCode() == 200) {
                    previewArea.setText("Backend Response: " + response.body());
                } else {
                    previewArea.setText("Error: " + response.body());
                }
            });
        } catch (Exception e) {
            SwingUtilities.invokeLater(() -> {
                previewArea.setText("Connection Error: " + e.getMessage() + "\n\nMake sure Python server is running on port 5000");
            });
        }
    }

    // Simulates scanning files using Python backend
    public void simulateScan(){

        String directory = (String) directoryBox.getSelectedItem();
        if (directory == null || directory.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Please select a directory first!");
            return;
        }

        previewArea.setText("Scanning... (connecting to Python backend)");

        // Simple JSON string without library
        String jsonData = "{\"directory\": \"" + directory.replace("\\", "\\\\") + "\"}";

        new Thread(() -> callPythonBackend("/scan", jsonData)).start();

        // Update progress bar
        for(int i=1;i<=100;i++){
            try{
                Thread.sleep(20);
            }catch(Exception e){}
            progressBar.setValue(i);
            scannedLabel.setText("Files Scanned: " + i);
        }
        etaLabel.setText("Scan Complete");
    }

    // Handles button clicks
    public void actionPerformed(ActionEvent e){

        // Browse button
        if(e.getSource()==browseBtn){

            int result = chooser.showOpenDialog(this);

            if(result==JFileChooser.APPROVE_OPTION){

                File selected = chooser.getSelectedFile();

                directoryBox.addItem(selected.getAbsolutePath());
                directoryBox.setSelectedItem(selected.getAbsolutePath());
            }
        }

        // Run scan button
        if(e.getSource()==runScanBtn){

            previewArea.setText("");
            progressBar.setValue(0);

            new Thread(() -> simulateScan()).start();
        }

        // Apply corrections button
        if(e.getSource()==applyBtn){

            previewArea.setText("Applying corrections... (connecting to Python backend)");

            // Simple JSON string without library
            String jsonData = String.format(
                    "{\"rules\": {" +
                            "\"naming\": %b, " +
                            "\"organize\": %b, " +
                            "\"group_similar\": %b, " +
                            "\"detect_duplicates\": %b, " +
                            "\"cleanup\": %b" +
                            "}}",
                    namingRule.isSelected(),
                    organizeRule.isSelected(),
                    customRule.isSelected(),
                    removeRule.isSelected(),
                    archiveRule.isSelected()
            );

            new Thread(() -> callPythonBackend("/apply_rules", jsonData)).start();

            JOptionPane.showMessageDialog(this,"Corrections Applied! Check preview area for details.");
        }
    }

    public static void main(String[] args) {
        new DataHygieneTool();
    }
}
