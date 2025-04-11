import json
import os
from pathlib import Path

def read_json_file(file_path):
    """Read a JSON file and return its contents as a Python dictionary."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def generate_automation_timeline_html(timeline_data):
    """Generate HTML for the automation timeline section."""
    html = '<div class="automation-timeline">\n'
    html += '    <h3>Automation Development Timeline</h3>\n'

    # Historical timeline entries
    for year, content in timeline_data['timeline']['historical'].items():
        html += f'    <div class="timeline-entry">\n'
        html += f'        <div class="timeline-year">{year}</div>\n'
        html += f'        <div class="timeline-content">\n'
        html += f'            <p>{content}</p>\n'
        html += f'        </div>\n'
        html += f'    </div>\n'

    # Predictions timeline entries
    for year, content in timeline_data['timeline']['predictions'].items():
        html += f'    <div class="timeline-entry">\n'
        html += f'        <div class="timeline-year">{year}</div>\n'
        html += f'        <div class="timeline-content">\n'
        html += f'            <p>{content}</p>\n'
        html += f'        </div>\n'
        html += f'    </div>\n'

    html += '</div>\n'
    return html

def generate_automation_challenges_html(challenges_data):
    """Generate HTML for the automation challenges section."""
    html = '<div class="automation-challenges">\n'
    html += f'    <h3>Current Automation Challenges</h3>\n'
    html += f'    <p>Despite significant progress, several challenges remain in fully automating the {challenges_data["challenges"]["topic"].split()[0].lower()} process:</p>\n'
    html += f'    <ul>\n'

    for challenge in challenges_data['challenges']['challenges']:
        # Split explanation into paragraphs if needed
        explanations = challenge['explanation'].split('  ')
        html += f'        <li><strong>{challenge["title"]}:</strong> {explanations[0]}</li>\n'

    html += f'    </ul>\n'
    html += '</div>\n'
    return html

def generate_standard_process_html(tree_data):
    """Generate HTML for the standard process tab content."""
    html = '<div id="standard-process" class="tab-content active">\n'

    # Process each top-level step in the tree
    for i, step in enumerate(tree_data['tree']['children']):
        html += f'    <div class="process-section">\n'
        html += f'        <h3>{i+1}. {step["step"]}</h3>\n'
        # Add a placeholder description
        html += f'        <p>This step involves {step["step"].lower()}.</p>\n'
        html += f'        <h4>Key Steps:</h4>\n'
        html += f'        <ul class="step-list">\n'

        # Add child steps if they exist
        if "children" in step:
            for child_step in step["children"]:
                html += f'            <li>{child_step["step"]}</li>\n'

        html += f'        </ul>\n'
        # Add a placeholder automation status
        html += f'        <p><strong>Automation Status:</strong> Currently being developed and refined.</p>\n'
        html += f'    </div>\n'

    # Add timeline and challenges sections
    html += '    {{TIMELINE_PLACEHOLDER}}\n'
    html += '    {{CHALLENGES_PLACEHOLDER}}\n'
    html += '</div>\n'
    return html


def generate_automation_pathway_html(adoption_data, implementation_data, roi_data):
    """Generate HTML for the automation pathway tab content."""
    html = '<div id="automation-pathway" class="tab-content">\n'

    # Automation Adoption Framework section
    html += '    <div class="process-section">\n'
    html += '        <h3>Automation Adoption Framework</h3>\n'
    html += '        <p>This framework outlines the pathway to full automation, detailing the progression from manual processes to fully automated systems.</p>\n'

    # Process each phase in the adoption data
    phase_keys = sorted([k for k in adoption_data.keys() if k.startswith('phase')])
    for phase_key in phase_keys:
        phase = adoption_data[phase_key]
        html += f'        <h4>{phase["title"]} ({phase["status"]})</h4>\n'
        html += '        <ul class="step-list">\n'
        for example in phase["examples"]:
            html += f'            <li>{example}</li>\n'
        html += '        </ul>\n'

    html += '    </div>\n'

    # Current Implementation Levels section
    html += '    <div class="process-section">\n'
    html += '        <h3>Current Implementation Levels</h3>\n'
    html += '        <p>The table below shows the current automation levels across different scales:</p>\n'
    html += '        <table class="automation-table">\n'
    html += '            <thead>\n'
    html += '                <tr>\n'
    html += '                    <th>Process Step</th>\n'
    html += '                    <th>Small Scale</th>\n'
    html += '                    <th>Medium Scale</th>\n'
    html += '                    <th>Large Scale</th>\n'
    html += '                </tr>\n'
    html += '            </thead>\n'
    html += '            <tbody>\n'

    # Correctly access the implementation data
    for step in implementation_data["implementation_assessment"]["process_steps"]:
        html += '                <tr>\n'
        html += f'                    <td>{step["step_name"]}</td>\n'
        html += f'                    <td>{step["automation_levels"]["low_scale"]}</td>\n'
        html += f'                    <td>{step["automation_levels"]["medium_scale"]}</td>\n'
        html += f'                    <td>{step["automation_levels"]["high_scale"]}</td>\n'
        html += '                </tr>\n'

    html += '            </tbody>\n'
    html += '        </table>\n'
    html += '    </div>\n'

    # ROI Analysis section - FIXED to match the actual JSON structure
    html += '    <div class="process-section">\n'
    html += '        <h3>Automation ROI Analysis</h3>\n'
    html += '        <p>The return on investment for automation depends on scale and production volume:</p>\n'
    html += '        <ul class="step-list">\n'

    # Correctly access the nested ROI timeframe data
    for scale in ["small_scale", "medium_scale", "large_scale"]:
        if scale in roi_data["roi_analysis"]:
            timeframe = roi_data["roi_analysis"][scale]["timeframe"]
            scale_display = scale.replace('_', ' ').title()
            html += f'            <li><strong>{scale_display}:</strong> {timeframe}</li>\n'

    html += '        </ul>\n'

    # Key benefits section unchanged
    if "key_benefits" in roi_data:
        html += '        <p>Key benefits driving ROI include ' + ', '.join(roi_data["key_benefits"][:-1]) + ', and ' + \
                roi_data["key_benefits"][-1] + '.</p>\n'

    html += '    </div>\n'
    html += '</div>\n'
    return html

def generate_technical_details_html(future_tech_data, specs_data):
    """Generate HTML for the technical details tab content."""
    html = '<div id="technical-details" class="tab-content">\n'

    # Automation Technologies section
    html += '    <div class="process-section">\n'
    html += '        <h3>Automation Technologies</h3>\n'
    html += '        <p>This section details the underlying technologies enabling automation.</p>\n'

    # Sensory Systems
    html += '        <h4>Sensory Systems</h4>\n'
    html += '        <ul class="step-list">\n'
    for sensor in future_tech_data["sensory_systems"]:
        html += f'            <li><strong>{sensor["name"]}:</strong> {sensor["description"]}</li>\n'
    html += '        </ul>\n'

    # Control Systems
    html += '        <h4>Control Systems</h4>\n'
    html += '        <ul class="step-list">\n'
    for control in future_tech_data["control_systems"]:
        html += f'            <li><strong>{control["name"]}:</strong> {control["description"]}</li>\n'
    html += '        </ul>\n'

    # Mechanical Systems
    html += '        <h4>Mechanical Systems</h4>\n'
    html += '        <ul class="step-list">\n'
    for mech in future_tech_data["mechanical_systems"]:
        html += f'            <li><strong>{mech["name"]}:</strong> {mech["description"]}</li>\n'
    html += '        </ul>\n'

    # Software Integration
    html += '        <h4>Software Integration</h4>\n'
    html += '        <ul class="step-list">\n'
    for software in future_tech_data["software_integration"]:
        html += f'            <li><strong>{software["name"]}:</strong> {software["description"]}</li>\n'
    html += '        </ul>\n'
    html += '    </div>\n'

    # Technical Specifications section
    html += '    <div class="process-section">\n'
    html += '        <h3>Technical Specifications for Commercial Automation</h3>\n'
    html += '        <p>Standard parameters for industrial production:</p>\n'

    # Performance Metrics
    html += '        <h4>Performance Metrics</h4>\n'
    html += '        <ul class="step-list">\n'
    for metric in specs_data["performance_metrics"]:
        html += f'            <li>{metric["name"]}: {metric["value"]} (Range: {metric["range"]})</li>\n'
    html += '        </ul>\n'

    # Implementation Requirements
    html += '        <h4>Implementation Requirements</h4>\n'
    html += '        <ul class="step-list">\n'
    for req in specs_data["implementation_requirements"]:
        html += f'            <li>{req["name"]}: {req["specification"]}</li>\n'
    html += '        </ul>\n'
    html += '    </div>\n'

    html += '</div>\n'
    return html

def generate_competing_approaches_html():
    """Generate HTML for the competing approaches tab content."""
    html = '<div id="competing-approaches" class="tab-content">\n'
    html += '    <div class="process-section">\n'
    html += '        <h3>Alternative Approaches</h3>\n'
    html += '        <p>These are alternative automation trees generated by different versions of our Iterative AI algorithm. Browse these competing models and vote for approaches you find most effective.</p>\n'
    html += '    </div>\n'

    # Approaches grid
    html += '    <div class="approaches-grid">\n'

    # Approach 1
    html += '        <div class="approach-card">\n'
    html += '            <h4>Efficiency-Optimized Approach</h4>\n'
    html += '            <p>This approach prioritizes minimizing resource usage and production time.</p>\n'
    html += '            <div class="approach-preview">\n'
    html += 'efficiency_optimized\n'
    html += '├── sensor_data_collection_8f29\n'
    html += '│   ├── lidar_scanning_a421\n'
    html += '│   └── camera_imaging_c731\n'
    html += '├── data_processing_d54f\n'
    html += '│   ├── object_detection_b651\n'
    html += '│   ├── path_planning_e922\n'
    html += '│   └── decision_making_f110\n'
    html += '├── control_execution_4a12\n'
    html += '└── monitoring_feedback_7b29</div>\n'
    html += '            <div class="approach-meta">\n'
    html += '                <p>Created by: Iterative AI v2.3</p>\n'
    html += '                <p>Votes: <span class="vote-count">18</span></p>\n'
    html += '            </div>\n'
    html += '            <div class="approach-actions">\n'
    html += '                <button class="button secondary vote-button">\n'
    html += '                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\n'
    html += '                        <path d="M12 4L18 10H6L12 4Z" fill="currentColor"/>\n'
    html += '                    </svg>\n'
    html += '                    Vote Up\n'
    html += '                </button>\n'
    html += '                <a href="#" class="button secondary">View Full Tree</a>\n'
    html += '            </div>\n'
    html += '        </div>\n'

    # Approach 2
    html += '        <div class="approach-card">\n'
    html += '            <h4>Safety-Optimized Approach</h4>\n'
    html += '            <p>This approach focuses on maximizing safety and reliability.</p>\n'
    html += '            <div class="approach-preview">\n'
    html += 'safety_optimized\n'
    html += '├── redundant_sensing_f721\n'
    html += '│   ├── primary_sensor_suite_a918\n'
    html += '│   ├── secondary_sensor_suite_c624\n'
    html += '│   └── failsafe_systems_d837\n'
    html += '├── validation_process_e542\n'
    html += '│   └── multi_level_verification_b213\n'
    html += '├── safety_protocols_9c31\n'
    html += '│   ├── emergency_procedures_a432\n'
    html += '│   ├── fault_detection_b548\n'
    html += '│   └── degraded_mode_operation_c659</div>\n'
    html += '            <div class="approach-meta">\n'
    html += '                <p>Created by: Iterative AI v2.4</p>\n'
    html += '                <p>Votes: <span class="vote-count">24</span></p>\n'
    html += '            </div>\n'
    html += '            <div class="approach-actions">\n'
    html += '                <button class="button secondary vote-button">\n'
    html += '                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\n'
    html += '                        <path d="M12 4L18 10H6L12 4Z" fill="currentColor"/>\n'
    html += '                    </svg>\n'
    html += '                    Vote Up\n'
    html += '                </button>\n'
    html += '                <a href="#" class="button secondary">View Full Tree</a>\n'
    html += '            </div>\n'
    html += '        </div>\n'

    # Approach 3
    html += '        <div class="approach-card">\n'
    html += '            <h4>Hybridized Approach</h4>\n'
    html += '            <p>This approach balances efficiency with safety considerations.</p>\n'
    html += '            <div class="approach-preview">\n'
    html += 'hybrid_system\n'
    html += '├── sensor_fusion_a329\n'
    html += '│   ├── multi_modal_sensing_b428\n'
    html += '│   ├── environmental_mapping_c529\n'
    html += '│   └── object_tracking_d630\n'
    html += '├── decision_making_e731\n'
    html += '│   ├── situation_assessment_f832\n'
    html += '│   ├── risk_evaluation_g933\n'
    html += '│   └── action_selection_h034</div>\n'
    html += '            <div class="approach-meta">\n'
    html += '                <p>Created by: Iterative AI v2.5</p>\n'
    html += '                <p>Votes: <span class="vote-count">42</span></p>\n'
    html += '            </div>\n'
    html += '            <div class="approach-actions">\n'
    html += '                <button class="button secondary vote-button">\n'
    html += '                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\n'
    html += '                        <path d="M12 4L18 10H6L12 4Z" fill="currentColor"/>\n'
    html += '                    </svg>\n'
    html += '                    Vote Up\n'
    html += '                </button>\n'
    html += '                <a href="#" class="button secondary">View Full Tree</a>\n'
    html += '            </div>\n'
    html += '        </div>\n'
    html += '    </div>\n'

    # Why Multiple Approaches section
    html += '    <div class="process-section">\n'
    html += '        <h3>Why Multiple Approaches?</h3>\n'
    html += '        <p>Different methodologies offer unique advantages depending on context:</p>\n'
    html += '        <ul class="step-list">\n'
    html += '            <li><strong>Scale considerations:</strong> Some approaches work better for large-scale production, while others are more suitable for specialized applications</li>\n'
    html += '            <li><strong>Resource constraints:</strong> Different methods optimize for different resources (time, computing power, energy)</li>\n'
    html += '            <li><strong>Quality objectives:</strong> Approaches vary in their emphasis on safety, efficiency, adaptability, and reliability</li>\n'
    html += '            <li><strong>Automation potential:</strong> Some approaches are more easily adapted to full automation than others</li>\n'
    html += '        </ul>\n'
    html += '        <p>By voting for approaches you find most effective, you help our community identify the most promising automation pathways.</p>\n'
    html += '    </div>\n'
    html += '</div>\n'

    return html

def generate_page_html(template_html, metadata, tree_data, timeline_data, challenges_data,
                       adoption_data, implementation_data, roi_data, future_tech_data, specs_data):
    """Generate the complete HTML page using the template and JSON data."""
    # Replace title, subtitle, and status
    new_html = template_html.replace('Bread Making', metadata['page_metadata']['title'])
    new_html = new_html.replace('<span>Bread Making</span>', f'<span>{metadata["page_metadata"]["title"]}</span>')
    new_html = new_html.replace('<span>Partial Automation Available</span>', f'<span>{metadata["page_metadata"]["automation_status"]}</span>')

    # Replace the subtitle (fixing the bread production issue)
    new_html = new_html.replace(
        '<p class="hero-subtitle">Exploring automation possibilities in artisanal and commercial bread production</p>',
        f'<p class="hero-subtitle">{metadata["page_metadata"]["subtitle"]}</p>'
    )

    # Replace progress bar (assuming 50% for partial automation, adjust as needed)
    progress_percentage = int(metadata['page_metadata']['automation_progress'].strip('%'))
    progress_style = f'style="width: {progress_percentage}%;"'
    new_html = new_html.replace('<div class="progress-fill"></div>', f'<div class="progress-fill" {progress_style}></div>')

    # Replace article summary
    summary_paragraphs = metadata['page_metadata']['explanatory_text'].split('\n\n')
    summary_html = ""
    for paragraph in summary_paragraphs:
        summary_html += f'<p>{paragraph}</p>\n'

    new_html = new_html.replace('<div class="article-summary">\n                        <p>Bread making is a multistep process that combines science and artistry. From gathering ingredients to the final rise and baking, each step presents unique automation opportunities. At present, commercial bakeries have achieved partial automation, with certain processes still benefiting from human expertise and intervention.</p>\n                        <p>This workflow breaks down the bread making process into manageable steps, illustrating both current automation capabilities and areas for future development.</p>\n                    </div>',
                      f'<div class="article-summary">\n{summary_html}</div>')

    # Generate tab content
    standard_process_html = generate_standard_process_html(tree_data)
    automation_pathway_html = generate_automation_pathway_html(adoption_data, implementation_data, roi_data)
    technical_details_html = generate_technical_details_html(future_tech_data, specs_data)
    competing_approaches_html = generate_competing_approaches_html()

    # Generate timeline and challenges HTML
    timeline_html = generate_automation_timeline_html(timeline_data)
    challenges_html = generate_automation_challenges_html(challenges_data)

    # Replace placeholders in standard process tab
    standard_process_html = standard_process_html.replace("{{TIMELINE_PLACEHOLDER}}", timeline_html)
    standard_process_html = standard_process_html.replace("{{CHALLENGES_PLACEHOLDER}}", challenges_html)

    # Replace tab content in the template
    tab_content_start = new_html.find('<!-- Standard Process Tab Content -->')
    tab_content_end = new_html.find('<!-- Footer placeholder to be filled by components.js -->')

    tab_content = (
        '<!-- Standard Process Tab Content -->\n'
        f'{standard_process_html}\n'
        '<!-- Automation Pathway Tab Content -->\n'
        f'{automation_pathway_html}\n'
        '<!-- Technical Details Tab Content -->\n'
        f'{technical_details_html}\n'
        '<!-- Competing Approaches Tab Content -->\n'
        f'{competing_approaches_html}\n'
        '                    <div class="contributors-section">\n'
        '                        <h3>Contributors</h3>\n'
        f'                        <p>This workflow was developed using Iterative AI analysis of {metadata["page_metadata"]["title"].lower()} processes with input from professional engineers and automation experts.</p>\n'
        '                        <p><em>Last updated: April 2024</em></p>\n'
        '                        <a href="#" class="button secondary" id="suggest-improvements">Suggest Improvements</a>\n'
        '                        \n'
        '                        <!-- Feedback form container (initially hidden) -->\n'
        '                        <div id="feedback-form-container" class="feedback-form-container">\n'
        '                            <h4>Suggest Improvements</h4>\n'
        f'                            <p>We value your input on how to improve this {metadata["page_metadata"]["title"].lower()} workflow. Please provide your suggestions below.</p>\n'
        '                            \n'
        '                            <form id="feedback-form" class="feedback-form">\n'
        '                                <div class="feedback-form-field">\n'
        '                                    <label for="feedback-name">Name (optional)</label>\n'
        '                                    <input type="text" id="feedback-name" name="name" placeholder="Your name">\n'
        '                                </div>\n'
        '                                \n'
        '                                <div class="feedback-form-field">\n'
        '                                    <label for="feedback-email">Email (optional)</label>\n'
        '                                    <input type="email" id="feedback-email" name="email" placeholder="your@email.com">\n'
        '                                </div>\n'
        '                                \n'
        '                                <div class="feedback-form-field">\n'
        '                                    <label for="feedback-subject">Subject</label>\n'
        '                                    <input type="text" id="feedback-subject" name="subject" placeholder="Brief description of your suggestion" required>\n'
        '                                </div>\n'
        '                                \n'
        '                                <div class="feedback-form-field">\n'
        '                                    <label for="feedback-body">Feedback Details</label>\n'
        '                                    <textarea id="feedback-body" name="message" placeholder="Please describe your suggestion in detail..." required></textarea>\n'
        '                                </div>\n'
        '                                \n'
        '                                <div class="feedback-actions">\n'
        '                                    <button type="button" id="cancel-feedback" class="button secondary">Cancel</button>\n'
        '                                    <button type="submit" id="send-feedback" class="button primary">Send Feedback</button>\n'
        '                                </div>\n'
        '                            </form>\n'
        '                            \n'
        '                            <div id="feedback-message" class="feedback-message"></div>\n'
        '                        </div>\n'
        '                    </div>\n'
    )

    new_html = new_html[:tab_content_start] + tab_content + new_html[tab_content_end:]

    # Update breadcrumb
    new_html = new_html.replace('<span><a href="/food-production/baking/index">Baking</a></span>',
                               '<span><a href="/transportation/autonomous-vehicles/index">Transportation</a></span>')

    return new_html

def main():
    # Define paths to JSON files
    templates_dir = "templates"
    metadata_path = os.path.join(templates_dir, "1. metadata.json")
    tree_path = os.path.join(templates_dir, "2. tree.json")
    timeline_path = os.path.join(templates_dir, "3. timeline.json")
    challenges_path = os.path.join(templates_dir, "4. challenges.json")
    adoption_path = os.path.join(templates_dir, "5. automation adoption.json")
    implementation_path = os.path.join(templates_dir, "6. current implementations.json")
    roi_path = os.path.join(templates_dir, "7. ROI analysis.json")
    future_tech_path = os.path.join(templates_dir, "8. Future Technology.json")
    specs_path = os.path.join(templates_dir, "9. Specifications Industrial.json")

    # Read template HTML
    with open("templates/breadmaking.html", "r", encoding="utf-8") as f:
        template_html = f.read()

    # Read JSON data
    metadata = read_json_file(metadata_path)
    tree_data = read_json_file(tree_path)
    timeline_data = read_json_file(timeline_path)
    challenges_data = read_json_file(challenges_path)
    adoption_data = read_json_file(adoption_path)["automation_adoption"]
    implementation_data = read_json_file(implementation_path)
    roi_data = read_json_file(roi_path)["roi_analysis"]
    future_tech_data = read_json_file(future_tech_path)["future_technology"]
    specs_data = read_json_file(specs_path)["industrial_specifications"]

    # Generate new HTML page
    new_html = generate_page_html(
        template_html,
        metadata,
        tree_data,
        timeline_data,
        challenges_data,
        adoption_data,
        implementation_data,
        roi_data,
        future_tech_data,
        specs_data
    )

    # Create output directory if it doesn't exist
    output_dir = "output"
    Path(output_dir).mkdir(exist_ok=True)

    # Write the generated HTML to a file
    output_file = os.path.join(output_dir, f"{metadata['page_metadata']['title'].lower().replace(' ', '_')}.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"Generated HTML page: {output_file}")

if __name__ == "__main__":
    main()